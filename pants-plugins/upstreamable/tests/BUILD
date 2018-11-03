python_tests(
  dependencies=[
    '3rdparty/py:pants',
  ],
)

perl6_library(
  name='perl6-test-lib',
  dependencies=[
    '3rdparty/perl6:csv-parser',
  ],
)

perl6_binary(
  name='perl6-test-bin',
  dependencies=[
    ':perl6-test-lib',
  ],
  script='run.p6',
)
