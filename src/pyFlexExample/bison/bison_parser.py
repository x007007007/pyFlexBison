from pyFlexBison.gen_bison import BisonGenerator, grammar
import jinja2


class BisonParserGenerator(BisonGenerator):
    res = None

    @grammar("""
        rules: rule        {#save_one_rule#}
            | rules rule   {#save_two_rules#}
            ;
        
        rule: WORD ':' exprs ';'  {##}
            ;
            
        exprs: expr                {#expr_to_exprs#}
            |  exprs '|' expr      {#exprs_append_expr#}
            ;
            
        expr: tokens    {#token_2_expr#}
            | tokens c_freg  {#token_with_c_parse#}
            ;
    
        tokens: WORD           {#token_one#}
            | tokens WORD      {#token_more#}
            ;
            
        c_freg: '{'  c_tokens '}'  {#c_freg#}
            ;
            
        c_token: WORD 
            | OTHER_TOKEN
            | ';'
            | '{'
            | '}'
            | '|'
            | ':'
            ;
        
        c_tokens: c_token
            | c_tokens c_token
            ;

    """, args_list=["$1", "$3"])
    def rule(self, name, rules, *args, **kwargs):
        print(f"result: {name}: {rules}")
        return dict(name=name, rules=rules)

    @rule.register(args_list=["$1"])
    def expr_to_exprs(self, a1, *args, **kwargs):
        print('expr_to_exprs')
        return [a1]

    @rule.register(args_list=["$1", "$3"])
    def exprs_append_expr(self, a1, a3):
        print(f'expr_to_exprs: {a1}, {a3}')
        return a1 + [a3]

    @rule.register(argc=1)
    def token_one(self, a1):
        print('token_one')

        return [a1]

    @rule.register(argc=2)
    def token_more(self, a1, a2):
        print(f'token_more {a1} {a2}')

        return a1 + [a2]

    @rule.register(argc=1)
    def token_2_expr(self, a1):
        print(f'token_2_expr: {a1}')
        return a1

    @rule.register(argc=2)
    def token_with_c_parse(self, tokens, c_token):
        print(f'token_with_c_parse: {tokens}, {c_token}')
        res = tokens + ['{##}']
        return res

    @rule.register(args_list=["$2"])
    def c_freg(self, c_freg):
        print(f'c_freg, {c_freg}')
        return "{#some_c_code#}"

    @rule.register(argc=1)
    def save_one_rule(self, rule):
        self.update_res(rule)

    @rule.register(argc=2)
    def save_two_rules(self, a1, a2):
        self.update_res(a2)

    def update_res(self, res):
        if self.res is None:
            self.res = []
        self.res.append(res)

    def done(self, success=False):
        print("hello")
        with open("res", "w") as fp:
            fp.write(self.to_text())

    def to_text(self):
        return jinja2.Template("""
{% for i in rules %}
{{i.name}}: {% for j in i.rules %}{{j | join:' '}}
          {% if loop.last %};{% else %}|    {% endif %} {% endfor %}
{% endfor %}
        """).render(self.res)
