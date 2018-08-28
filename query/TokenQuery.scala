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

final object KeywordReservedWord extends TokenType

// For symbol tokens. What passes for a "symbol" varies across languages.
final object Symbol extends TokenType

sealed trait Operator extends TokenType
final object BasicOperator extends TokenType
final object AssignmentOperator extends TokenType

// Any indexing punctuation, including the '.' in ".<field>", and the square brackets in e.g.
// "[<number>]" and "[<string>]".
sealed trait FieldExtractionOperator extends TokenType
final object DotOperator extends FieldExtractionOperator
final object ArrowOperator extends FieldExtractionOperator
// TODO: this is supposed to be something to find e.g. python_dict['asdf'] as an instance of
// dereferencing a field 'asdf'.
final object IndexStartOperator extends FieldExtractionOperator

sealed trait NewScope extends TokenType
final object BasicNewScope extends NewScope

// This just records the mere fact that a function is invoked -- this usually happens with parens,
// e.g. `myFun()` -- this just records the fact that there were open parens after an expression.
final object FunctionCall extends TokenType

sealed abstract class ClosePrevious[T <: TokenType](base: T) extends TokenType
final object IndexEnd extends ClosePrevious(IndexStartOperator)
final object ScopeClose extends ClosePrevious(BasicNewScope)
final object FunctionCallEnd extends ClosePrevious(FunctionCall)

sealed trait Literal extends TokenType
final object StringLiteral extends Literal
final object CharLiteral extends Literal
final object NumericLiteral extends Literal

// Things I can't figure out how to fit into other categories right now.
sealed trait Misc extends TokenType
final object Colon extends Misc
// TODO: this should be closed by e.g. Colon, but only optionally (if there is no TernaryStart, then
// it is interpreted as a label). How do we formalize this?
final object TernaryStart extends Misc
final object Semicolon extends Misc
