from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import re

from builtins import object

from future.utils import text_type

from pants.base.exceptions import TargetDefinitionException
from pants.build_graph.target import Target
from pants.util.memo import memoized_property
from pants.util.objects import Exactly, datatype


# TODO: document this
PERL6_INSTALL_DIR_PREFIX = 'inst#'


class ZefRequirement(datatype([
    ('module_name', text_type),
    ('version_spec', Exactly(text_type, type(None))),
])):

  @classmethod
  def alias(cls):
    return 'zef_requirement'

  # TODO: this will reject many legal module names!
  _allowed_module_name_pattern = re.compile(r'\A([a-zA-Z]+)::([a-zA-Z]+)\Z')

  def __new__(cls, module_name, version_spec=None):
    if not cls._allowed_module_name_pattern.match(module_name):
      raise self.make_type_error("invalid Zef module name '{}': must match '{}'."
                                 .format(module_name, cls._allowed_module_name_pattern.pattern))

    return super(ZefRequirement, cls).__new__(cls, module_name, version_spec)

  @memoized_property
  def zef_identity_spec(self):
    if self.version_spec is not None:
      return '{}:ver<{}>'.format(self.module_name, self.version_spec)
    else:
      return module_name


class ZefRequirementLibrary(Target):

  @classmethod
  def alias(cls):
    return 'zef_requirement_library'

  def __init__(self, requirements=None, **kwargs):
    if not requirements:
      raise TargetDefinitionException(self, "requirements kwarg empty or not given: {!r}"
                                      .format(requirements))
    super(ZefRequirementLibrary, self).__init__(**kwargs)
