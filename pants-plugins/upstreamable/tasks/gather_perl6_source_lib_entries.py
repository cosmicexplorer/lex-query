from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os

from pants.base.build_environment import get_buildroot
from pants.base.exceptions import TaskError
from pants.task.task import Task
from pants.util.objects import Exactly, datatype
from twitter.common.collections import OrderedSet
from upstreamable.targets.perl6_library import Perl6Library
from upstreamable.targets.zef_requirement_library import \
    PERL6_INSTALL_DIR_PREFIX


class GatherPerl6SourceLibEntries(Task):

  source_target_constraint = Exactly(Perl6Library)

  class Entries(datatype([('containing_lib_dirs', tuple)])): pass

  class GatherEntriesError(TaskError): Exception

  @classmethod
  def product_types(cls):
    return [cls.Entries]

  def execute(self):
    # TODO: figure out if using an OrderedSet here breaks anyone's assumptions about PERL6LIB
    # entries!
    # TODO: figure out if using an OrderedSet here is necessary!
    all_lib_dirs = OrderedSet()
    source_lib_targets = self.context.targets(self.source_target_constraint.satisfied_by)
    for lib_tgt in source_lib_targets:
      all_lib_dirs.update(
        os.path.normpath(os.path.join(get_buildroot(), os.path.dirname(s)))
        for s in lib_tgt.sources_relative_to_buildroot())
    if source_lib_targets and (not all_lib_dirs):
      raise self.GatherEntriesError(
        "No containing directories found for source_lib_targets {!r}. "
        "Do these targets all contain no sources?"
        .format(source_lib_targets))
    else:
      for normalized_lib_dir_path in all_lib_dirs:
        assert(not normalized_lib_dir_path.startswith(PERL6_INSTALL_DIR_PREFIX))
      self.context.products.register_data(self.Entries,
                                          self.Entries(containing_lib_dirs=tuple(all_lib_dirs)))
