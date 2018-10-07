from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import logging
import os

from future.utils import binary_type
from pants.base.workunit import WorkUnitLabel
from pants.binaries.binary_tool import Script
from pants.invalidation.cache_manager import VersionedTargetSet
from pants.subsystem.subsystem import Subsystem
from pants.util.dirutil import is_writable_dir, safe_mkdir
from pants.util.memo import memoized_method, memoized_property
from pants.util.objects import datatype
from pants.util.process_handler import subprocess
from pants.util.strutil import create_path_env_var, safe_shlex_join
from upstreamable.subsystems.rakudo_moar import RakudoMoar
from upstreamable.subsystems.rakudobrew import Rakudobrew
from upstreamable.targets.zef_requirement_library import \
    PERL6_INSTALL_DIR_PREFIX

logger = logging.getLogger(__name__)


class Zef(Script):
  options_scope = 'zef'

  default_version = '0.5.3'

  class ZefException(Exception): pass

  @classmethod
  def subsystem_dependencies(cls):
    return super(Zef, cls).subsystem_dependencies() + (
      RakudoMoar.scoped(cls),
      Rakudobrew.scoped(cls),
    )

  @memoized_property
  def _rakudobrew(self):
    return Rakudobrew.scoped_instance(self)

  @memoized_property
  def _rakudo_moar(self):
    return RakudoMoar.scoped_instance(self)

  _executable_filename = 'zef'

  @memoized_property
  def _bin_dir(self):
    maybe_bin_install_dir = os.path.join(self._rakudo_moar.select(), 'install/share/perl6/site/bin')
    if 0 == len(os.listdir(maybe_bin_install_dir)):
      # This is an empty directory -- we need to bootstrap zef.
      self._rakudobrew.install_zef()
    exe_filenames = os.listdir(maybe_bin_install_dir)
    if self._executable_filename not in exe_filenames:
      raise self.ZefException(
        "Error: '{}' not found in '{}' with contents {!r}."
        .format(self._executable_filename, maybe_bin_install_dir, exe_filenames))

    return maybe_bin_install_dir

  class ZefInstallRequest(datatype([
      ('zef_requirements', tuple),
      ('into_dir', binary_type),
  ])):

    def __new__(cls, zef_requirements, into_dir):
      # Non-empty iterable of requirements.
      if not zef_requirements:
        raise self.make_type_error(
          "Error: no zef requirements were provided to install into dir '{}'."
          .format(into_dir))

      if not is_writable_dir(into_dir):
        raise self.make_type_error(
          "Error: provided directory path '{}' does not exist or is not writable."
          .format(into_dir))

      # TODO: Remove the need to specify the containing class explicitly!
      return super(Zef.ZefInstallRequest, cls).__new__(
        cls, tuple(zef_requirements), binary_type(into_dir))

    @memoized_property
    def as_install_spec(self):
      # NB: See https://github.com/ugexe/zef for more info.
      return '{}{}'.format(PERL6_INSTALL_DIR_PREFIX, self.into_dir)

  class ZefInstallResult(datatype([('install_spec', binary_type)])):

    def __new__(cls, install_spec):
      return super(Zef.ZefInstallResult, cls).__new__(cls, binary_type(install_spec))

  @memoized_property
  def path_entries(self):
    return [self._bin_dir] + self._rakudo_moar.path_entries

  def resolve(self, workdir, invalidation_check, workunit_factory):
    # Install all of the resolve specs at once, into a single dir which has a name determined by
    # the fingerprint of all the relevant targets in the transitive closure.
    # NB: Obtaining the dir name is currently our only use of the VersionedTargetSet.
    resolve_vts = VersionedTargetSet.from_versioned_targets(invalidation_check.all_vts)
    vts_results_dir = os.path.join(workdir, resolve_vts.cache_key.hash)
    safe_mkdir(vts_results_dir)

    all_zef_reqs = []
    for zef_vt in invalidation_check.all_vts:
      all_zef_reqs.extend(zef_vt.target.requirements)
    install_request = self.ZefInstallRequest(
      zef_requirements=all_zef_reqs,
      into_dir=vts_results_dir)

    if invalidation_check.invalid_vts or not resolve_vts.valid:
      install_result = self._install_requirements(install_request, workunit_factory)
    else:
      # No-op -- we have a (hopefully) well-formed install dir at this location already.
      install_result = self.ZefInstallResult(install_request.as_install_spec)

    return install_result

  def _run_zef_command(self, workunit_factory, argv):
    subproc_env = os.environ.copy()
    subproc_env['PATH'] = create_path_env_var(self.path_entries, subproc_env, prepend=True)

    all_argv = ['zef'] + argv
    pretty_printed_argv = safe_shlex_join(all_argv)
    try:
      with workunit_factory() as workunit:
        return subprocess.check_call(
          all_argv,
          env=subproc_env,
          stdout=workunit.output('stdout'),
          stderr=workunit.output('stderr'))
    except (OSError, subprocess.CalledProcessError) as e:
      raise self.ZefException(
        "Error with zef command '{}': {}"
        .format(pretty_printed_argv, e),
        e)

  def _install_requirements(self, install_request, workunit_factory):
    # NB: See https://github.com/ugexe/zef for more info.
    identities = [req.zef_identity_spec for req in install_request.zef_requirements]
    install_spec = install_request.as_install_spec
    # Raise on nonzero exit.
    self._run_zef_command(workunit_factory, [
      '--install-to={}'.format(install_spec),
      # TODO: do we need to run update beforehand? Check https://github.com/ugexe/zef!
      'install',
    ] + identities)

    return self.ZefInstallResult(install_spec)
