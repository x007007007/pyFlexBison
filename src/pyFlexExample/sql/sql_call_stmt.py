from pyFlexBison.gen_bison import BisonGenerator, grammar

class SqlCallStmt():

    @grammar("""
        call_stmt:
              CALL_SYM sp_name opt_paren_expr_list {##}
            ;
        opt_paren_expr_list: 
            /* Empty */ {#opt_paren_expr_list_empty#}
            | '(' opt_expr_list ')' {#opt_paren_expr_list#}
            ;
        
    """, args_list=['$2', '$3'])
    def call_stmt(self):
        return None

    @call_stmt.registor()
    def opt_paren_expr_list_empty(self):
        pass

    @call_stmt.registor()
    def opt_paren_expr_list(self):
        pass