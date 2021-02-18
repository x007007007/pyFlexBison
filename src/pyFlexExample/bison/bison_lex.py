from pyFlexBison.gen_flex import FlexGenerator



class BisonLexGenerator(FlexGenerator):

    ext_config = FlexGenerator.trim_rules_string("""
        
    """)

    token_rule_split = ":=:"
    token_rule = FlexGenerator.trim_rules_string(r"""
        "/*"[^(*/)]*?"*/"               {   int len=strlen(yytext); for(int i=0;i<len;i++){ if(yytext[i] == '\n'){lineno++;} }  ECHO;}
        "//"[^\n]*                      { ECHO;}
                
        [a-zA-Z0-9_]+                   :=: WORD
        \'.\'                           :=: WORD
        %[a-zA-Z0-9_]                    :=: WORD
        
        "{"                             :=: '{'
        "}"                             :=: '}'
        ":"                             :=: ':'
        ";"                             :=: ';'
        "|"                             :=: '|'
        [ \t]                           { ; }

        \n                          { printf("=========>lineno %d\n", lineno++);}
        .                             :=: OTHER_TOKEN
    """)


