from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os

from pants.subsystem.subsystem import Subsystem


class Perl5(Subsystem):
  options_scope = 'perl5'

  # TODO: make this configurable!
  default_bin_path = '/usr/bin/perl'
  bin_dir = os.path.dirname(default_bin_path)
