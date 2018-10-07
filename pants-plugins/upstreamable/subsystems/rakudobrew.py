from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import logging
import os

from pants.binaries.binary_tool import Script
from pants.binaries.binary_util import BinaryRequest
from pants.scm.git import Git
from pants.scm.scm import Scm
from pants.util.dirutil import is_readable_dir, safe_mkdir
from pants.util.memo import memoized_method, memoized_property
from pants.util.process_handler import subprocess
from pants.util.strutil import create_path_env_var, safe_shlex_join
from upstreamable.subsystems.perl5 import Perl5

logger = logging.getLogger(__name__)


class Rakudobrew(Script):
  options_scope = 'rakudobrew'

  default_version = 'bdd060c8886da6049f87ea30fdc01dc457747a18'

  class RakudoBrewBootstrapError(Exception): pass

  @classmethod
  def subsystem_dependencies(cls):
    return super(Rakudobrew, cls).subsystem_dependencies() + (Perl5.scoped(cls),)

  @memoized_property
  def _perl5(self):
    return Perl5.scoped_instance(self)

  @memoized_property
  def path_entries(self):
    return [
      os.path.join(self.select(), 'bin'),
      self._perl5.bin_dir,
    ]

  def _run_rakudobrew_command(self, argv):
    subproc_env = os.environ.copy()
    subproc_env['PATH'] = create_path_env_var(self.path_entries, subproc_env, prepend=True)

    all_argv = ['rakudobrew'] + argv
    pretty_printed_argv = safe_shlex_join(all_argv)
    try:
      return subprocess.check_output(
        all_argv,
        env=subproc_env)
    except (OSError, subprocess.CalledProcessError) as e:
      raise self.RakudoBrewBootstrapError(
        "Error with rakudobrew command '{}': {}"
        .format(pretty_printed_argv, e),
        e)

  def install_zef(self):
    output = self._run_rakudobrew_command(['build', 'zef'])
    logger.info("output from installing zef:\n{}".format(output))

  def switch_tool(self, tool_name, version):
    """We'll want to do this for our moar subsystem."""
    known_dirname = '{}-{}'.format(tool_name, version)
    # This is a fast command to run on no-op.
    output = self._run_rakudobrew_command(['switch', known_dirname])
    logger.debug("output from switching to configuration '{}':\n{}"
                 .format(known_dirname, output))

  def build_tool_into(self, tool_name, version):
    known_dirname = '{}-{}'.format(tool_name, version)
    expected_dir = os.path.join(self.select(), known_dirname)
    # Build it.
    if not os.path.isdir(expected_dir):
      logger.info("building tool '{}' at version '{}'...".format(tool_name, version))
      output = self._run_rakudobrew_command(['build', tool_name, version])
      logger.info("output from building tool '{}' at version '{}':\n{}"
                  .format(tool_name, version, output))
      if not is_readable_dir(expected_dir):
        raise self.RakudoBrewBootstrapError(
          "The expected directory after building tool '{}' at version '{}' is '{}', but that path "
          "does not exist or is not writable."
          .format(tool_name, version, expected_dir))

    return expected_dir

  @memoized_method
  def select(self, *args, **kwargs):
    """Returns a directory which can be added to the PATH to use the rakudobrew tools."""
    download_path = self._safe_get_download_dir_path()
    # If the directory is empty, clone into it (this is allowed for empty existing
    # directories). Otherwise, assume the clone was already performed.
    if len(os.listdir(download_path)) == 0:
      self._do_clone_and_checkout(download_path)
    return download_path

  _GIT_CLONE_HTTPS_URL = 'https://github.com/tadzik/rakudobrew'

  def _do_clone_and_checkout(self, download_path):
    desired_sha = self.version()
    try:
      checkout = Git.clone(self._GIT_CLONE_HTTPS_URL, download_path)
      checkout.set_state(desired_sha)
    except Scm.ScmException as e:
      raise self.RakudoBrewBootstrapError(
        "Error checking out revision '{}' from {}: {}"
        .format(desired_sha, self._GIT_CLONE_HTTPS_URL, e),
        e)

  @memoized_method
  def _safe_get_download_dir_path(self):
    """Ensures the directory exists for the current version before returning its path."""
    version = self.version()
    binary_request = self._make_binary_request(version)
    host_platform = self._binary_util._host_platform()
    # Because archive_type=None, this will be a path to a file, but we are going to be cloning into
    # a directory.
    fake_file_download_relpath = binary_request.get_download_path(host_platform)
    dir_download_relpath = os.path.dirname(fake_file_download_relpath)

    bootstrap_dir = os.path.realpath(os.path.expanduser(self.get_options().pants_bootstrapdir))
    full_download_dir_path = os.path.join(bootstrap_dir, dir_download_relpath)
    safe_mkdir(full_download_dir_path)
    return full_download_dir_path
