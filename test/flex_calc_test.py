from pyFlexBison.flex import FlexGenerator


class AddFlexGenerator(FlexGenerator):
    token_rule = r"""
        "+"     = ADD
        "-"     = SUB
        "*"     = MUL
        "/"     = DIV
        "|"     = ABS
        [0-9]+  = NUMBER
        \n      = EOL
        [ \t]   = 
    """

    def t_number(self, token: str) -> int:
        return int(token)


