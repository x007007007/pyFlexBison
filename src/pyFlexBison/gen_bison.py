import typing
import re
import warnings
from collections import OrderedDict
from .generator import GeneratorBase


class GrammarRegister:
    def __init__(self, rule_string, func):
        self.func = func
        self.rule_string = rule_string.strip()
        self.sub_func_map = {}

    def __repr__(self):
        return f"\n{self.rule_string}"

    def __call__(self, name=None):
        def decorate(func):
            nonlocal name
            if name is None:
                name = func.__name__
            self.sub_func_map[name] = func
            return func
        return decorate

    def generate(self):
        pass

def grammar(rule_string):
    rule_string = GeneratorBase.trim_rules_string(rule_string)
    def decorate(func):
        func.register = GrammarRegister(rule_string, func)
        return func
    return decorate


class BisonGenerator(GeneratorBase):
    MAC_BREW_PATH = '/usr/local/opt/bison/bin/bison'
    bin_path: str = None
    bison_version: typing.Tuple[int, int, int] = None
    bison_bin: str = None
    run_env: typing.Dict[str, str]

    def __init__(self):
        self.rules = []
        self.load_rules()

    def load_rules(self):
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method):
                if (reg := getattr(method, 'register', None)) and isinstance(reg, GrammarRegister):
                    self.rules.append(reg)
        return self.rules

    def generate_rule(self):
        return "\n".join(i for i in self.rules)

    def generate(self) -> str:
        template = Template(self.trim_rules_string("""
        %{
            #include <stdio.h>
        %}
        %token NUMBER ADD SUB MUL DIV ABS EOL

        %%
        $rules
        %%
        
        int main(int argc, char **argv) {
            yyparse();
            return 0;
        }
        
        //定义解析出错时的处理
        void yyerror(char *s) {
            fprintf(stderr, "error: %s\n", s);
        }
        """))
        return template.substitute(
            rules=self.generate_rule(),
        )