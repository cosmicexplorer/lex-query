package lex_query.lex

import lex_query.query._

import ammonite.ops._
import com.twitter.util._

import scala.util.matching._
import scala.util.matching.Regex.Match

class TokenLexError(message: String, base: Option[Throwable] = None)
    extends Exception(message, base.getOrElse(null))

case class TokenMatchInfo(source: Regex, theMatch: Match)

case class FiletypeInfo(path: Path)

trait LexerForFiletype {
  def isApplicable(fileInfo: FiletypeInfo): Boolean
  def searchRegexps: Seq[Regex]
  def resolveMatchToToken(t: TokenMatchInfo): Try[TokenType]
}

object LexerForFiletype {
  type TokenResolver = TokenMatchInfo => Try[TokenType]
}

case class InvalidLexerSpecification(message: String) extends TokenLexError(message)

case class MapLexer(
  fileMatchers: Seq[Regex],
  matchActions: Map[Regex, TokenType],
) extends LexerForFiletype {

  override def isApplicable(fileInfo: FiletypeInfo): Boolean = {
    val filePath = fileInfo.path.toString
    val noneMatched = fileMatchers.flatMap(_.findFirstMatchIn(filePath)).isEmpty
    !noneMatched
  }

  override val searchRegexps: Seq[Regex] = matchActions.keys.toSeq

  override def resolveMatchToToken(t: TokenMatchInfo): Try[TokenType] = matchActions
    .get(t.source)
    .map(Return(_))
    .getOrElse(Throw(InvalidLexerSpecification(
      s"regex ${t.source} was not found in matchActions: ${matchActions}.")))
}

object KnownLexers {
  implicit class MatchExt(t: TokenMatchInfo) {
    def matchString: Try[String] = Option(t.theMatch.matched)
      .map(Return(_))
      .getOrElse(Throw(InvalidLexerSpecification(s"null match string for match in ${t}")))
  }

  val KnownCKeywords = Seq(
    "auto",
    "break",
    "case",
    "char",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extern",
    "float",
    "for",
    "goto",
    "if",
    "int",
    "long",
    "register",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "struct",
    "switch",
    "typedef",
    "union",
    "unsigned",
    "void",
    "volatile",
    "while",
  )

  val AllOperators = Seq(
    "+",
    "-",
    "*",
    "^",
    ",",
    "++",
    "--",
    "==",
    "!=",
    "<",
    ">",
    "<=",
    ">=",
    "&",
    "&&",
    "|",
    "||",
    "%",
    "~",
    "!",
  )

  val AssignmentOperators = Seq(
    ">>=",
    "<<=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "^=",
    "&=",
    "|=",
  )

  def regexFromStrings(strings: Seq[String]): Regex = strings
    .map(Regex.quote)
    .foldLeft(None: Option[String])({
      case (None, rxStr) => Some(rxStr)
      case (Some(rest), rxStr) => Some(s"$rest|$rxStr")
    })
    .head
    .r

  val C = MapLexer(
    fileMatchers = Seq("*.c$".r),
    matchActions = Map(
      regexFromStrings(KnownCKeywords) -> KeywordReservedWord,
      regexFromStrings(AllOperators) -> BasicOperator,
      regexFromStrings(AssignmentOperators) -> AssignmentOperator,
      "[a-zA-Z_][a-zA-Z_0-9]*".r -> Symbol,
      "\\.".r -> DotOperator,
      "->".r -> ArrowOperator,
      "\\[".r -> IndexStartOperator,
      "\\]".r -> IndexEnd,
      "\\{".r -> BasicNewScope,
      "\\}".r -> ScopeClose,
      "\\(".r -> FunctionCall,
      "\\)".r -> FunctionCallEnd,
      "\"(?:[^\"]|\\\\|\\\")*\"".r -> StringLiteral,
      "0[xX][a-fA-F0-9]+[uUlL]?".r -> NumericLiteral,
      "0[0-9]+[uUlL]*".r -> NumericLiteral,
      "[a-zA-Z_]?'(?:[^']|\\\\|\\')+'".r -> CharLiteral,
      "[0-9]+(?:[Ee][+-]?[0-9]+)[fFlL]?".r -> NumericLiteral,
      "[0-9]*\\.[0-9]+(?:[Ee][+-]?[0-9]+)?[fFlL]?".r -> NumericLiteral,
      "[0-9]+\\.[0-9]*(?:[Ee][+-]?[0-9]+)?[fFlL]?".r -> NumericLiteral,
      ":".r -> Colon,
      "\\?".r -> TernaryStart,
      ";".r -> Semicolon,
    ))
}
