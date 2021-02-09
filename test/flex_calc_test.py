from pyFlexBison.gen_flex import FlexGenerator


def test_flex_generator_inherit_token():
    class CalcFlexGenerator(FlexGenerator):
        token_rule = r"""
            "+"     = ADD
        """
    calc_flex = CalcFlexGenerator()
    lex_container = calc_flex.generate_rule()
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
    lex_container = calc_flex.generate_rule()
    print(lex_container)
    assert lex_container == r"""
"+"     {  return ADD;  }
[0-9]+     {  callback_token_process("t_number");/* */ return NUMBER;  }
    """.strip()


def test_flex_generator_env_check():
    flex = FlexGenerator()
    flex.env_checker()
    assert flex.flex_version is not None



def test_flex_generator_env_build():
    class Calc1FlexGenerator(FlexGenerator):
        token_rule = r"""
            "+"     = ADD
            [0-9]+  = NUMBER 
        """

        def t_number(self, token: str) -> int:
            return int(token)

    calc1 = Calc1FlexGenerator()
    calc1.env_checker()
    calc1.build()
