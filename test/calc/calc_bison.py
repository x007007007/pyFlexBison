from pyFlexBison.gen_bison import BisonGenerator, grammar


class CalcBisonGenerator(BisonGenerator):
    @grammar("""
        calclist:
            | calclist exp EOL {##} 
            ;
    """)
    def calclist(self, *args, **kwargs):
        print(args[1])

    @grammar("""
        exp: term {##} //表达式:=项
            | exp ADD term {#exp_add#} //或者，表达式::=表达式+项
            | exp SUB term {#exp_sub#} //或者，表达式::=表达式-项
            ;
    """)
    def exp_add_sub(self):
        pass

    @exp_add_sub.register()
    def exp_add(self):
        pass

    @exp_add_sub.register()
    def exp_sub(self):
        pass

    @grammar("""
        term: factor {##} //项::=因子
            | term MUL factor {#term_mul_factor#} //或者，项::=项*因子
            | term DIV factor {#term_div_factor#} //或者，项::=项/因子
            ;
        factor: NUMBER {##} //因子::=数字
            | ABS factor {#abs_factor#} //或者，因子::=绝对值.因子
            ;
    """)
    def term_and_factor(self, a1):
        return a1

    @term_and_factor.register()
    def term_mul_factor(self, a1, a2, a3):
        return a1 * a3

    @term_and_factor.register()
    def term_div_factor(self, a1, a2, a3):
        return a1 / a3

    @term_and_factor.register()
    def abs_factor(self, a1, a2):
        return abs(a2)
