from pyFlexBison.gen_flex import FlexGenerator


def test_flex_generator_inherit_token():
    class CalcFlexGenerator(FlexGenerator):
        token_rule = r"""
            "+"     = ADD
        """
    calc_flex = CalcFlexGenerator()
    lex_container = calc_flex.generate()
    assert lex_container == r"""
        "+"     {  return ADD;  }
    """.strip()


def test_flex_generator_inherit_method():
    class Calc1FlexGenerator(FlexGenerator):
        token_rule = r"""
            "+"     = ADD
            [0-9]+  = NUMBER 
        """

        def t_number(self, token: str) -> int:
            return int(token)

    calc_flex = Calc1FlexGenerator()
    lex_container = calc_flex.generate()
    print(lex_container)
    assert lex_container == r"""
"+"     {  return ADD;  }
[0-9]+     {  callback_token_process("t_number");/* */ return NUMBER;  }
    """.strip()