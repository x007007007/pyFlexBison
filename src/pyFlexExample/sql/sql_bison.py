from pyFlexBison.gen_bison import BisonGenerator, grammar


class SqlBisonGenerator(BisonGenerator):
    @grammar("""
        calclist:
            | calclist exp EOL {##} 
            ;
    """, args_list=["$2"])
    def calclist(self, a2, *args, **kwargs):
        return a2


    @grammar("""
        exp: term {##} //表达式:=项
            | exp ADD term {#exp_add#} //或者，表达式::=表达式+项
            | exp SUB term {#exp_sub#} //或者，表达式::=表达式-项
            ;
    """, argc=1)
    def exp_add_sub(self, a1, *args, **kwargs):
        return a1

    @exp_add_sub.register(argc=3)
    def exp_add(selfa1, a1, a2, a3, *args, **kwargs):
        return a1 + a3

    @exp_add_sub.register(argc=3)
    def exp_sub(self, a1, a2, a3, *args, **kwargs):
        return a1 - a3

    @grammar("""
        term: factor {##} //项::=因子
            | term MUL factor {#term_mul_factor#} //或者，项::=项*因子
            | term DIV factor {#term_div_factor#} //或者，项::=项/因子
            ;
        factor: NUMBER {##} //因子::=数字
            | ABS factor {#abs_factor#} //或者，因子::=绝对值.因子
            ;
    """, argc=1)
    def term_and_factor(self, a1):
        print("this is python code")
        return a1

    @term_and_factor.register(argc=3)
    def term_mul_factor(self, a1, a2, a3):
        return a1 * a3

    @term_and_factor.register(argc=3)
    def term_div_factor(self, a1, a2, a3):
        return a1 / a3

    @term_and_factor.register(argc=2)
    def abs_factor(self, a1, a2):
        return abs(a2)
