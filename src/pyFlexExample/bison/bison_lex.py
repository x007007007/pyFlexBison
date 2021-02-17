from pyFlexBison.gen_flex import FlexGenerator



class BisonLexGenerator(FlexGenerator):

    ext_config = FlexGenerator.trim_rules_string("""

    """)

    token_rule_split = ":=:"
    token_rule = FlexGenerator.trim_rules_string(r"""
        "//"[^\n]*                      { ECHO;}
                
        [a-zA-Z_]+                      :=: WORD
        \'.\'                           :=: WORD
        %[a-zA-Z0-9]                    :=: WORD
        
        "{"                             :=: '{'
        "}"                             :=: '}'
        ":"                             :=: ':'
        ";"                             :=: ';'
        "|"                             :=: '|'
        [ \t]                           { ; }

        [\n\r]                       :=:
        .                             :=: OTHER_TOKEN
    """)


