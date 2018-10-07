from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os

from pants.base.exceptions import TargetDefinitionException
from pants.base.payload import Payload
from pants.build_graph.target import Target
from pants.engine.legacy.structs import BaseGlobs
from pants.option.custom_types import GlobExpansionConjunction
from pants.source.payload_fields import SourcesField
from pants.source.wrapped_globs import LazyFilesetWithSpec
from pants.util.collections import assert_single_element


class Perl6Binary(Target):

  script_file_ext = '.p6'

  @classmethod
  def alias(cls):
    return 'perl6_binary'

  def _ignore_validate_fn(self, fileset_with_spec): return fileset_with_spec

  def __init__(self, script=None, sources=None, address=None, payload=None,  **kwargs):
    if sources is not None:
      raise TargetDefinitionException(self, "sources must be None: was {!r}.".format(sources))
    elif script and script.endswith(self.script_file_ext):
      script_relpath_buildroot = os.path.join(address.spec_path, script)
      base_globs = BaseGlobs.from_sources_field([script_relpath_buildroot], address.spec_path)
      fileset_with_spec = LazyFilesetWithSpec(address.spec_path, base_globs.filespecs,
                                              lambda: [script])
    else:
      raise TargetDefinitionException(
        self,
        "script argument '{}' to {}() must end in '{}'."
        .format(script, self.alias(), self.script_file_ext))

    payload = payload or Payload()
    payload.add_fields({
      'sources': SourcesField(fileset_with_spec, address),
    })
    super(Perl6Binary, self).__init__(address=address, payload=payload, **kwargs)

  @property
  def script_path(self):
    return assert_single_element(self.sources_relative_to_buildroot())
