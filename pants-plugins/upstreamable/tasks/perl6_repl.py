from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os
import signal

from pants.task.repl_task_mixin import ReplTaskMixin
from pants.util.contextutil import signal_handler_as
from pants.util.memo import memoized_property
from pants.util.objects import Exactly
from pants.util.process_handler import subprocess
from upstreamable.subsystems.perl6 import Perl6
from upstreamable.subsystems.zef import Zef, ZefReplBootstrap
from upstreamable.targets.perl6_library import Perl6Library
from upstreamable.targets.zef_requirement_library import (ZefRequirement,
                                                          ZefRequirementLibrary)
from upstreamable.tasks.collect_perl6_env import CollectPerl6Env


class Perl6Repl(ReplTaskMixin):

  @classmethod
  def subsystem_dependencies(cls):
    return super(Perl6Repl, cls).subsystem_dependencies() + (
      Perl6.scoped(cls),
      ZefReplBootstrap.scoped(cls),
    )

  @memoized_property
  def _perl6(self):
    return Perl6.scoped_instance(self)

  @memoized_property
  def _repl_bootstrap(self):
    return ZefReplBootstrap.scoped_instance(self)

  source_target_constraint = Exactly(Perl6Library, Zef.ZefInstallResult)

  @classmethod
  def select_targets(cls, target):
    # TODO: This override is required for MutexTaskMixin (which ReplTaskMixin subclasses) -- I'm not
    # exactly sure what that task is for yet.
    return cls.source_target_constraint.satisfied_by(target)

  @classmethod
  def prepare(cls, options, round_manager):
    super(Perl6Repl, cls).prepare(options, round_manager)
    round_manager.require_data(CollectPerl6Env.Perl6Env)

  def setup_repl_session(self, targets):
    # NB: `targets` is unused, as it is just for the purposes of MutexTaskMixin.
    perl6_env = self.context.products.get_data(CollectPerl6Env.Perl6Env)
    all_zef_resolves = perl6_env.zef_resolve_results + (
      self._repl_bootstrap.install_result_for_repl_bootstrap,
    )
    return perl6_env.copy(zef_resolve_results=all_zef_resolves)

  def launch_repl(self, perl6_env):
    # TODO: this is a massive hack that should be removed from python_repl.py (this is the leading
    # cause of interactivity issues in america!).
    def ignore_control_c(signum, frame): pass

    with signal_handler_as(signal.SIGINT, ignore_control_c):
      # When called with no arguments, drops into a repl.
      return self._perl6.invoke_perl6([], perl6_env)
