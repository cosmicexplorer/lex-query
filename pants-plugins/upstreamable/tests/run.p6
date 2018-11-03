use CSV::Parser;

use some_module;

say CSV::Parser;
say Foo;
say "hey";

sub MAIN ( Str  :$file    = "file.dat"
         , Num  :$length  = Num(24)
         , Bool :$verbose = False
         )
{
    $file.say;
    $length.say;
    $verbose.say;
}
