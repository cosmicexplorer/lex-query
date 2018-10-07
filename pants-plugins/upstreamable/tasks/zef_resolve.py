from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os

from pants.base.exceptions import TaskError
from pants.base.workunit import WorkUnitLabel
from pants.invalidation.cache_manager import VersionedTargetSet
from pants.task.task import Task
from pants.util.dirutil import safe_mkdir
from pants.util.memo import memoized_property
from pants.util.objects import Exactly

from upstreamable.subsystems.zef import Zef
from upstreamable.targets.zef_requirement_library import ZefRequirementLibrary


class ZefResolve(Task):

  source_target_constraint = Exactly(ZefRequirementLibrary)

  @classmethod
  def product_types(cls):
    return [Zef.ZefInstallResult]

  class ZefResolveError(TaskError): pass

  @classmethod
  def subsystem_dependencies(cls):
    return super(ZefResolve, cls).subsystem_dependencies() + (Zef.scoped(cls),)

  @memoized_property
  def _zef(self):
    return Zef.scoped_instance(self)

  def _resolve_workunit_factory(self, *args, **kwargs):
    return self.context.new_workunit(
      name='zef-resolve',
      labels=[WorkUnitLabel.TOOL],
      *args, **kwargs)

  # NB: Manually manage cache target dirs with VersionedTargetSet!
  # TODO: This is one of those resolves (like python, jvm, ???) which uses all the relevant targets
  # in the current run (i.e. all transitive deps of target roots) to form the resolve. This can be
  # confusing!
  def execute(self):
    zef_req_libs = self.context.targets(self.source_target_constraint.satisfied_by)
    with self.invalidated(zef_req_libs, invalidate_dependents=True) as zef_invalidation_check:
      # If there are no targets in play, don't do the resolve.
      if zef_invalidation_check.all_vts:
        try:
          install_result = self._zef.resolve(
            self.workdir, zef_invalidation_check, self._resolve_workunit_factory)
          self.context.products.register_data(Zef.ZefInstallResult, install_result)
        except Zef.ZefException as e:
          raise self.ZefResolveError(
            "Error resolving zef req libs: {}".format(e),
            e)
