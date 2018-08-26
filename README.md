lex-query
=========

Query token structures across languages to perform the functions of an LSP server, without any "semantic" info.

# Links
- [LSP Protocol v2.0](https://github.com/Microsoft/language-server-protocol/blob/master/versions/protocol-2-x.md)

# TODO
- how to describe token queries that make sense?
    - define a set of common functionality for identifying a language
- how to efficiently store token indices that will allow token queries to be Pretty Fast?
    - what kind of queries and what kind of input?
- how to describe lexical grammars for languages and sublanguages?
    - how to identify the common classes of token structures, as in, to someone writing queries?

# License
[GPL 3.0+](./LICENSE)
