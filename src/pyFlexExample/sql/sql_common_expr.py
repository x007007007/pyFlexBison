from pyFlexBison.gen_bison import BisonGenerator, grammar


class SqlCommonExpr():

    @grammar("""
        copt_expr_list:
            /* empty */ {##}
            | expr_list
        ;

        expr_list: expr {#expr_list#}
            | expr_list ',' expr {#expr_list_append#}
        ;
        
        expr:
              expr or expr %prec OR_SYM             {#expr_bool#}
            | expr XOR expr %prec XOR               {#expr_bool#}
            | expr and expr %prec AND_SYM           {#expr_bool#}
            | NOT_SYM expr %prec NOT_SYM            {#expr_bool#}
            | bool_pri IS TRUE_SYM %prec IS         {#expr_is_bool#}
            | bool_pri IS not TRUE_SYM %prec IS     {#expr_is_not_bool#}
            | bool_pri IS FALSE_SYM %prec IS        {#expr_is_bool#}
            | bool_pri IS not FALSE_SYM %prec IS    {#expr_is_not_bool#}
            | bool_pri IS UNKNOWN_SYM %prec IS      {#expr_is_bool#}
            | bool_pri IS not UNKNOWN_SYM %prec IS  {#expr_is_not_bool#}
            | bool_pri %prec SET_VAR 
            ;

    """, args_list=['$2', '$3'])
    def copt_expr_list(self):
        return None

    @copt_expr_list.register(argc=1)
    def expr_list(self, a):
        return [a]

    @copt_expr_list.register(argv_list=['$1', '$3'])
    def expr_list_append(self, a, b):
        return a + b

    @copt_expr_list.register()
    def copt_expr_list(self):
        pass

    @copt_expr_list.register()
    def expr_bool(self):
        pass

    @copt_expr_list.register()
    def expr_bool(self):
        pass

    @copt_expr_list.register()
    def expr_is_bool(self):
        pass

    @copt_expr_list.register()
    def expr_is_not_bool(self):
        pass