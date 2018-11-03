from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

from pants.base.build_environment import pants_version


class PantsAllRequirements(object):
  """Context-aware object factory to wrap pants deps at the current pants version."""

  alias = 'pants_all_requirements'

  def __init__(self, parse_context):
    self._parse_context = parse_context

  def __call__(self, name='pants', with_testinfra=False):
    cur_pants_version = pants_version()
    all_reqs = []

    pants_req = self._parse_context.create_object(
      'python_requirement',
      'pantsbuild.pants=={}'.format(cur_pants_version))
    all_reqs.append(pants_req)

    if with_testinfra:
      testinfra_req = self._parse_context.create_object(
        'python_requirement',
        'pantsbuild.pants.testinfra=={}'.format(cur_pants_version))
      all_reqs.append(testinfra_req)

    self._parse_context.create_object(
      'python_requirement_library',
      name=name,
      requirements=[pants_req] + all_reqs)
