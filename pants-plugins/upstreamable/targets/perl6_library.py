from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os

from pants.base.build_environment import get_buildroot
from pants.base.payload import Payload
from pants.build_graph.target import Target
from pants.util.memo import memoized_property


class Perl6Library(Target):

  default_sources_globs = '*.pm6'

  @classmethod
  def alias(cls):
    return 'perl6_library'

  def __init__(self,
               address=None,
               payload=None,
               sources=None,
               **kwargs):
    payload = payload or Payload()
    payload.add_fields({
      'sources': self.create_sources_field(sources, address.spec_path, key_arg='sources'),
    })
    super(Perl6Library, self).__init__(address=address, payload=payload, **kwargs)

  @memoized_property
  def lib_dirs(self):
    return [
      os.path.normpath(
        os.path.join(
          get_buildroot(),
          os.path.dirname(source_file_path)))
      for source_file_path in self.sources_relative_to_buildroot()
    ]
