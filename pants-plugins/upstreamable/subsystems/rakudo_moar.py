from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os

from pants.binaries.binary_tool import NativeTool
from pants.util.dirutil import is_readable_dir
from pants.util.memo import memoized_method, memoized_property
from upstreamable.subsystems.rakudobrew import Rakudobrew


class RakudoMoar(NativeTool):
  """Wraps a rakudo implementation with the MoarVM backend."""

  options_scope = 'rakudo-moar'

  moar_tool_name = 'moar'

  default_version = '2d7724f8bca3648c219b925c6729b1dc8f55881d'

  class RakudoMoarException(Exception): pass

  @classmethod
  def subsystem_dependencies(cls):
    return super(RakudoMoar, cls).subsystem_dependencies() + (Rakudobrew.scoped(cls),)

  @memoized_property
  def _rakudobrew(self):
    return Rakudobrew.scoped_instance(self)

  _install_bin_rel_path = 'install/bin'

  @memoized_property
  def install_bin_dir(self):
    return os.path.join(self.select(), self._install_bin_rel_path)

  @memoized_property
  def path_entries(self):
    return [self.install_bin_dir] + self._rakudobrew.path_entries

  _expected_executable_files = frozenset(['moar', 'nqp', 'perl6'])

  @memoized_method
  def select(self, *args, **kwargs):
    version = self.version()
    moar_build_output_dir = self._rakudobrew.build_tool_into(self.moar_tool_name, version)
    expected_bin_dir = os.path.join(moar_build_output_dir, self._install_bin_rel_path)
    if not is_readable_dir(expected_bin_dir):
      raise self.RakudoMoarException(
        "The directory at '{}' should now contain moar at version '{}', but that path does not "
        "exist or is not writable."
        .format(expected_bin_dir, version))
    else:
      exe_files = os.listdir(expected_bin_dir)
      remaining_files = self._expected_executable_files - frozenset(exe_files)
      if remaining_files:
        raise self.RakudoMoarException(
          "The directory '{}' was expected to contain at least {!r}, but contained {!r}. "
          "Missing files: {!r}."
          .format(expected_bin_dir, sorted(list(self._expected_executable_files)), exe_files,
                  sorted(list(remaining_files))))
      else:
        # Default to this version of MoarVM -- tools like Zef use this implicitly.
        self._rakudobrew.switch_tool(self.moar_tool_name, version)
        # Return the top-level containing directory -- `self._bin_dir` contains the path to the
        # binaries.
        return moar_build_output_dir
