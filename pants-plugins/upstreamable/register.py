from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

from pants.build_graph.build_file_aliases import BuildFileAliases
from pants.goal.task_registrar import TaskRegistrar as task
from upstreamable.targets.pants_all_requirements import PantsAllRequirements
from upstreamable.targets.perl6_binary import Perl6Binary
from upstreamable.targets.perl6_library import Perl6Library
from upstreamable.targets.zef_requirement_library import (ZefRequirement,
                                                          ZefRequirementLibrary)
from upstreamable.tasks.collect_perl6_env import CollectPerl6Env
from upstreamable.tasks.gather_perl6_source_lib_entries import \
    GatherPerl6SourceLibEntries
from upstreamable.tasks.perl6_repl import Perl6Repl
from upstreamable.tasks.perl6_run import Perl6Run
from upstreamable.tasks.zef_resolve import ZefResolve


def build_file_aliases():
  return BuildFileAliases(
    context_aware_object_factories={
      PantsAllRequirements.alias: PantsAllRequirements,
    },
    objects={
      ZefRequirement.alias(): ZefRequirement,
    },
    targets={
      Perl6Binary.alias(): Perl6Binary,
      Perl6Library.alias(): Perl6Library,
      ZefRequirementLibrary.alias(): ZefRequirementLibrary,
    },
  )


def register_goals():
  task(name='perl6', action=Perl6Repl).install('repl')
  task(name='requirements', action=ZefResolve).install('resolve')
  task(name='sources', action=GatherPerl6SourceLibEntries).install('perl6-prep')
  task(name='perl6-env', action=CollectPerl6Env).install('perl6-prep')
  task(name='perl6', action=Perl6Run).install('run')
