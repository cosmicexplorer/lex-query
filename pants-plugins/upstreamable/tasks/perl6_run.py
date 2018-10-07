from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os
import signal

from pants.base.exceptions import TaskError
from pants.base.workunit import WorkUnitLabel
from pants.task.task import Task
from pants.util.memo import memoized_property
from pants.util.objects import Exactly
from pants.util.process_handler import subprocess
from pants.util.strutil import safe_shlex_join, safe_shlex_split
from upstreamable.subsystems.perl6 import Perl6
from upstreamable.subsystems.zef import Zef, ZefReplBootstrap
from upstreamable.targets.perl6_binary import Perl6Binary
from upstreamable.tasks.collect_perl6_env import CollectPerl6Env


class Perl6Run(Task):

  class Perl6RunError(TaskError): pass

  @classmethod
  def register_options(cls, register):
    super(Perl6Run, cls).register_options(register)
    register('--args', type=list, help='Run with these extra args to the main script.')

  @classmethod
  def supports_passthru_args(cls):
    return True

  @classmethod
  def subsystem_dependencies(cls):
    return super(Perl6Run, cls).subsystem_dependencies() + (Perl6.scoped(cls),)

  @memoized_property
  def _perl6(self):
    return Perl6.scoped_instance(self)

  @classmethod
  def prepare(cls, options, round_manager):
    super(Perl6Run, cls).prepare(options, round_manager)
    round_manager.require_data(CollectPerl6Env.Perl6Env)

  def _run_workunit_factory(self, *args, **kwargs):
    return self.context.new_workunit(
      name='perl6-run',
      # TODO: this doesn't have any output with ./pants -q run cli:bin?
      labels=[WorkUnitLabel.TOOL, WorkUnitLabel.RUN],
      *args, **kwargs)

  source_target_constraint = Exactly(Perl6Binary)

  def execute(self):
    binary = self.require_single_root_target()
    if not self.source_target_constraint.satisfied_by(binary):
      return

    extra_args = []
    for arg in self.get_options().args:
      extra_args.extend(safe_shlex_split(arg))
    passthru_args = self.get_passthru_args()
    full_argv = extra_args + [binary.script_path, '--'] + passthru_args

    perl6_env = self.context.products.get_data(CollectPerl6Env.Perl6Env)

    self.context.release_lock()

    try:
      self._perl6.invoke_perl6(
        full_argv,
        perl6_env,
        workunit_factory=self._run_workunit_factory)
    except Perl6.Perl6InvocationError as e:
      raise self.Perl6RunError(
        "Error running perl 6: {}".format(e),
        e,
        exit_code=e.exit_code)
