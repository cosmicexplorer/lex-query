from __future__ import (absolute_import, division, generators, nested_scopes,
                        print_function, unicode_literals, with_statement)

from pants_test.pants_run_integration_test import PantsRunIntegrationTest


class TestPerl6RunIntegrationTest(PantsRunIntegrationTest):

  _p6_run_target = 'pants-plugins/upstreamable/tests:perl6-test-bin'

  def test_perl6_run(self):
    pants_run = self.run_pants(['-q', 'run', self._p6_run_target])
    self.assert_success(pants_run)
    self.assertEqual(pants_run.stdout_data, """\
(Parser)
(Foo)
hey
file.dat
24
False
""")
