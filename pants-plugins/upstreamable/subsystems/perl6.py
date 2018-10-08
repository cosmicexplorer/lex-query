from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import logging
import os

from pants.subsystem.subsystem import Subsystem
from pants.util.memo import memoized_property
from pants.util.process_handler import subprocess
from pants.util.strutil import create_path_env_var, ensure_binary, safe_shlex_join
from upstreamable.subsystems.rakudo_moar import RakudoMoar


logger = logging.getLogger(__name__)


class Perl6(Subsystem):
  options_scope = 'perl6'

  class Perl6InvocationError(Exception):

    def __init__(self, msg, exit_code=None, *args, **kwargs):
      self.exit_code = exit_code
      super(Perl6.Perl6InvocationError, self).__init__(msg, *args, **kwargs)

  @classmethod
  def subsystem_dependencies(cls):
    return super(Perl6, cls).subsystem_dependencies() + (RakudoMoar.scoped(cls),)

  @memoized_property
  def _rakudo_moar(self):
    return RakudoMoar.scoped_instance(self)

  # NB: For PERL5LIB on perl 5, this is ':', but perl 6 uses a comma.
  PERL6LIB_SEP = ','

  def _get_perl6_subproc_os_env(self, perl6_env):
    # NB: These source file containing directory paths are assumed to have been de-duped.
    source_lib_containing_dirs = list(perl6_env.source_lib_entries.containing_lib_dirs)
    zef_install_specs = [r.install_spec for r in perl6_env.zef_resolve_results]

    # NB: put the thirdparty resolve at the end.
    all_lib_entries = source_lib_containing_dirs + zef_install_specs
    perl6lib_joined = ensure_binary(self.PERL6LIB_SEP.join(map(ensure_binary, all_lib_entries)))

    full_path_var = create_path_env_var(self._rakudo_moar.path_entries, os.environ.copy(),
                                        prepend=True)

    invocation_env = os.environ.copy()
    invocation_env.update({
      'PERL6LIB': perl6lib_joined,
      'PATH': full_path_var,
    })

    return invocation_env

  # TODO: make this configurable to allow the use of e.g. perl6-gdb-m!
  _perl6_exe_filename = 'perl6'

  def invoke_perl6(self, argv, perl6_env, workunit_factory=None):
    full_argv = [self._perl6_exe_filename] + list(argv)
    subproc_env = self._get_perl6_subproc_os_env(perl6_env)

    pretty_printed_argv = safe_shlex_join(full_argv)
    try:
      logger.debug('running perl6 comand {!r} with env {!r}'.format(full_argv, subproc_env))
      if workunit_factory:
        with workunit_factory(cmd=pretty_printed_argv) as workunit:
          # TODO: should we be catching KeyboardInterrupt or something?
          return subprocess.check_call(
            full_argv,
            env=subproc_env,
            stdout=workunit.output('stdout'),
            stderr=workunit.output('stderr'))
      else:
        return subprocess.check_call(full_argv, env=subproc_env)
    except (OSError, subprocess.CalledProcessError) as e:
      raise self.Perl6InvocationError(
        "Error with perl6 command '{}': {}".format(pretty_printed_argv, e),
        e,
        exit_code=e.returncode)
