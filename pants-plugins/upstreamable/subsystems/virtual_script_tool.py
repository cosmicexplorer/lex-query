from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

import os

from pants.binaries.binary_tool import Script
from pants.util.dirutil import safe_mkdir
from pants.util.memo import memoized_method


class VirtualScriptTool(Script):
  """For `Script`s which need a place to download, but don't have a single archive URL (requiring
  workarounds).
  """

  @memoized_method
  def safe_get_download_dir_path(self):
    """Ensures the directory exists for the current version before returning its path."""
    version = self.version()
    binary_request = self._make_binary_request(version)
    host_platform = self._binary_util._host_platform()
    # Because archive_type=None, this will be a path to a file, but we are going to be cloning into
    # a directory.
    fake_file_download_relpath = binary_request.get_download_path(host_platform)
    dir_download_relpath = os.path.dirname(fake_file_download_relpath)

    bootstrap_dir = os.path.realpath(os.path.expanduser(self.get_options().pants_bootstrapdir))
    full_download_dir_path = os.path.join(bootstrap_dir, dir_download_relpath)
    safe_mkdir(full_download_dir_path)
    return full_download_dir_path
