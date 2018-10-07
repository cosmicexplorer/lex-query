use CSV::Parser;

class Foo {
  sub zape () { say "zipi" }
  class Bar {
    method baz () { return 'Þor is mighty' }
    our &zape = { "zipi" };
    our $quux = 42;
  }
}

our $foo is export = 3;
