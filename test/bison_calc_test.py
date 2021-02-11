from pyFlexBison.gen_bison import BisonGenerator, grammar
from unittest import mock


def test_flex_generator_inherit_token():
    class CalcBisonGenerator(BisonGenerator):
        @grammar("""
            calclist:
                | calclist exp EOL {##} 
                ;
        """, argc=3)
        def calclist(self, *args, **kwargs):
            print(args[1])

        @grammar("""
            exp: term {##} //表达式:=项
                | exp ADD term {#exp_add#} //或者，表达式::=表达式+项
                | exp SUB term {#exp_sub#} //或者，表达式::=表达式-项
                ;
        """, argc=1)
        def exp_add_sub(self):
            pass

        @exp_add_sub.register(argc=3)
        def exp_add(self):
            pass

        @exp_add_sub.register(argc=3)
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
        """, argc=1)
        def term_and_factor(self, a1):
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

    calc_bison = CalcBisonGenerator()
    calc_bison.env_checker()

    assert isinstance(calc_bison.rules, list)
    assert len(calc_bison.rules) == 3
    assert calc_bison.tokens == set(['MUL', 'DIV', 'EOL', 'NUMBER', 'SUB', 'ADD', 'ABS'])

    calc_bison.build()



def test_flex_generator_generate():
    class CalcBisonGenerator(BisonGenerator):
        @grammar("""
            calclist:
                | calclist exp EOL {##} 
                ;
        """, argc=3)
        def calclist(self, *args, **kwargs):
            print(args[1])

        @grammar("""
            exp: term {##} //表达式:=项
                | exp ADD term {#exp_add#} //或者，表达式::=表达式+项
                | exp SUB term {#exp_sub#} //或者，表达式::=表达式-项
                ;
        """, argc=1)
        def exp_add_sub(self):
            pass

        @exp_add_sub.register(argc=3)
        def exp_add(self):
            pass

        @exp_add_sub.register(argc=3)
        def exp_sub(self):
            pass

    calc = CalcBisonGenerator()
    res = calc.generate()
    assert isinstance(res, str)
