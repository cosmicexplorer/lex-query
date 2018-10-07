from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

from pants.base.workunit import WorkUnitLabel
from pants.invalidation.cache_manager import VersionedTargetSet
from pants.task.task import Task
from pants.util.memo import memoized_method, memoized_property
from pants.util.objects import Exactly, datatype
from pants.util.process_handler import subprocess
from pants.util.strutil import ensure_binary

from upstreamable.subsystems.zef import Zef
from upstreamable.targets.perl6_library import Perl6Library
from upstreamable.targets.zef_requirement_library import ZefRequirementLibrary
from upstreamable.tasks.gather_perl6_source_lib_entries import GatherPerl6SourceLibEntries
from upstreamable.tasks.zef_resolve import ZefResolve


class CollectPerl6Env(Task):

  @classmethod
  def prepare(cls, options, round_manager):
    super(CollectPerl6Env, cls).prepare(options, round_manager)
    round_manager.require_data(GatherPerl6SourceLibEntries.Entries)
    round_manager.require_data(Zef.ZefInstallResult)

  @classmethod
  def product_types(cls):
    return [cls.Perl6Env]

  class Perl6Env(datatype([
      ('source_lib_entries', GatherPerl6SourceLibEntries.Entries),
      ('zef_resolve_result', Exactly(Zef.ZefInstallResult, type(None))),
  ])): pass

  def execute(self):
    env = self.Perl6Env(
      source_lib_entries=self.context.products.get_data(GatherPerl6SourceLibEntries.Entries),
      zef_resolve_result=self.context.products.get_data(Zef.ZefInstallResult))
    self.context.products.register_data(self.Perl6Env, env)
