from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os

from pants.subsystem.subsystem import Subsystem
from pants.util.memo import memoized_property
from pants.util.process_handler import subprocess
from pants.util.strutil import create_path_env_var, ensure_binary
from upstreamable.subsystems.rakudo_moar import RakudoMoar


class Perl6(Subsystem):
  options_scope = 'perl6'

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

  def invoke_perl6_synchronously(self, argv, perl6_env):
    full_argv = [self._perl6_exe_filename] + list(argv)
    os_env = self._get_perl6_subproc_os_env(perl6_env)
    return subprocess.check_call(full_argv, env=os_env)
