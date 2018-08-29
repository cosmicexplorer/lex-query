from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

from pants.build_graph.build_file_aliases import BuildFileAliases
from pants.goal.task_registrar import TaskRegistrar as task
from upstreamable.targets.custom_scala_dependencies import \
    CustomScalaDependencies


def build_file_aliases():
  return BuildFileAliases(
    context_aware_object_factories={
      CustomScalaDependencies.alias(): CustomScalaDependencies,
    },
  )
