import unittest


class LexerTestCase(unittest.TestCase):
    def makeLexer(self, text):
        from spi import Lexer
        lexer = Lexer(text)
        return lexer

    def test_tokens(self):
        from spi import (
            INTEGER_CONST, REAL_CONST, MUL, INTEGER_DIV, FLOAT_DIV, PLUS, MINUS, LPAREN, RPAREN,
            ASSIGN, DOT, ID, SEMI, BEGIN, END, PROCEDURE
        )
        records = (
            ('234', INTEGER_CONST, 234),
            ('3.14', REAL_CONST, 3.14),
            ('*', MUL, '*'),
            ('DIV', INTEGER_DIV, 'DIV'),
            ('/', FLOAT_DIV, '/'),
            ('+', PLUS, '+'),
            ('-', MINUS, '-'),
            ('(', LPAREN, '('),
            (')', RPAREN, ')'),
            (':=', ASSIGN, ':='),
            ('.', DOT, '.'),
            ('number', ID, 'number'),
            (';', SEMI, ';'),
            ('BEGIN', BEGIN, 'BEGIN'),
            ('END', END, 'END'),
            ('PROCEDURE', PROCEDURE, 'PROCEDURE'),
        )
        for text, tok_type, tok_val in records:
            lexer = self.makeLexer(text)
            token = lexer.get_next_token()
            self.assertEqual(token.type, tok_type)
            self.assertEqual(token.value, tok_val)


class InterpreterTestCase(unittest.TestCase):
    def makeInterpreter(self, text):
        from spi import Lexer, Parser, SymbolTableBuilder, Interpreter
        lexer = Lexer(text)
        parser = Parser(lexer)
        tree = parser.parse()
        symtab_builder = SymbolTableBuilder()
        symtab_builder.visit(tree)


        interpreter = Interpreter(tree)
        return interpreter

    def test_integer_arithmetic_expressions(self):
        for expr, result in (
            ('3', 3),
            ('2 + 7 * 4', 30),
            ('7 - 8 DIV 4', 5),
            ('14 + 2 * 3 - 6 DIV 2', 17),
            ('7 + 3 * (10 DIV (12 DIV (3 + 1) - 1))', 22),
            ('7 + 3 * (10 DIV (12 DIV (3 + 1) - 1)) DIV (2 + 3) - 5 - 3 + (8)', 10),
            ('7 + (((3 + 2)))', 12),
            ('- 3', -3),
            ('+ 3', 3),
            ('5 - - - + - 3', 8),
            ('5 - - - + - (3 + 4) - +2', 10),
        ):
            interpreter = self.makeInterpreter(
                """PROGRAM Test;
                   VAR
                       a : INTEGER;
                   BEGIN
                       a := %s
                   END.
                """ % expr
            )
            interpreter.interpret()
            globals = interpreter.GLOBAL_MEMORY
            self.assertEqual(globals['a'], result)

    def test_float_arithmetic_expressions(self):
        for expr, result in (
            ('3.14', 3.14),
            ('2.14 + 7 * 4', 30.14),
            ('7.14 - 8 / 4', 5.14),
        ):
            interpreter = self.makeInterpreter(
                """PROGRAM Test;
                   VAR
                       a : REAL;
                   BEGIN
                       a := %s
                   END.
                """ % expr
            )
            interpreter.interpret()
            globals = interpreter.GLOBAL_MEMORY
            self.assertEqual(globals['a'], result)

    def test_expression_invalid_syntax_01(self):
        with self.assertRaises(Exception):
            self.makeInterpreter(
            """
            PROGRAM Test;
            VAR
                a : INTEGER;
            BEGIN
               a := 10 * ;  {Invalid syntax}
            END.
            """
            )

    def test_expression_invalid_syntax_02(self):
        with self.assertRaises(Exception):
            self.makeInterpreter(
            """
            PROGRAM Test;
            VAR
                a : INTEGER;
            BEGIN
               a := 1 (1 + 2); {Invalid syntax}
            END.
            """
            )

    def test_program(self):
        text = """\
PROGRAM Part12;
VAR
   number : INTEGER;
   a, b   : INTEGER;
   y      : REAL;

PROCEDURE P1;
VAR
   a : REAL;
   k : INTEGER;
   PROCEDURE P2;
   VAR
      a, z : INTEGER;
   BEGIN {P2}
      z := 777;
   END;  {P2}
BEGIN {P1}

END;  {P1}

BEGIN {Part12}
   number := 2;
   a := number ;
   b := 10 * a + 10 * number DIV 4;
   y := 20 / 7 + 3.14
END.  {Part12}
"""
        interpreter = self.makeInterpreter(text)
        interpreter.interpret()

        globals = interpreter.GLOBAL_MEMORY
        self.assertEqual(len(globals.keys()), 4)
        self.assertEqual(globals['number'], 2)
        self.assertEqual(globals['a'], 2)
        self.assertEqual(globals['b'], 25)
        self.assertAlmostEqual(globals['y'], float(20) / 7 + 3.14)  # 5.9971...


if __name__ == '__main__':
    unittest.main()
