package lex_query.query

sealed trait TokenType

// We can literally do Boyer-Moore string search on the tokens themselves, wouldn't that be absurd??
case class TokenSequence(tokens: Seq[TokenType]) {

  def append(t: TokenType): TokenSequence = joinWith(TokenSequence.init(t))
  def :+(t: TokenType): TokenSequence = append(t)

  type TokenSeqJoiner = (TokenSequence, TokenSequence) => TokenSequence
  implicit val concatJoiner: TokenSeqJoiner = (a, b) => TokenSequence(a.tokens ++ b.tokens)

  def joinWith(t: TokenSequence)(implicit f: TokenSeqJoiner): TokenSequence = f(this, t)
  def ++(t: TokenSequence)(implicit f: TokenSeqJoiner): TokenSequence = joinWith(t)(f)
}

object TokenSequence {
  def init(t: TokenType): TokenSequence = TokenSequence(Seq(t))
}

// For symbol tokens. What passes for a "symbol" varies across languages.
final case class Symbol(name: String) extends TokenType
// Any indexing punctuation, including the '.' in ".<field>", and the square brackets in e.g.
// "[<number>]" and "[<string>]".
abstract class FieldExtractionOperator extends TokenType
final case class DotOperator(field: Symbol) extends FieldExtractionOperator
// TODO: this is supposed to be something to find e.g. python_dict['asdf'] as an instance of
// dereferencing a field 'asdf'.
final case class IndexOperator(arg: String) extends FieldExtractionOperator
// Words like "def" in python, as well as e.g. assignments with "=". E.g. "var"/"val" in scala.
final case class Definition(name: String) extends TokenType
// This just records the mere fact that a function is invoked -- this usually happens with parens,
// e.g. `myFun()` -- this just records the fact that there were open parens after an expression.
final object FunctionCall extends TokenType
