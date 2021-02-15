from pyFlexBison.gen_flex import FlexGenerator



class CalcFlexGenerator(FlexGenerator):
    token_rule = FlexGenerator.trim_rules_string(r"""
        "+"     = ADD
        "-"     = SUB
        "*"     = MUL
        "/"     = DIV
        "|"     = ABS
        [0-9]+  = NUMBER
        \n      = EOL
        [ \t]   = 
    """)

    def t_number(self, token: str) -> int:
        return int(token)

