import typing
import re
import warnings
from string import Template
from .generator import GeneratorBase


class GrammarRegister:
    def __init__(self, rule_string, func):
        self.__tokens = set()
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

    @property
    def tokens(self):
        return self.__tokens

    def analysis_rules(self):
        self.callback_name_set = set()
        res = re.findall(r"\s([A-Z_]+)\s", self.rule_string, re.M | re.S)
        self.__tokens = set(res)
        self.callback_replace = dict()
        for name_replace_hold in re.findall(r"{#\w*?#}", self.rule_string, re.M | re.S):
            callback_name = name_replace_hold[2:-2]
            if callback_name == '':
                callback_method = self.func
            else:
                callback_method = self.sub_func_map.get(callback_name, None)
            if not callback_method:
                raise SyntaxError(f"requirement a not exist callback: {callback_name}")
            else:
                self.callback_replace[name_replace_hold] = callback_method

    def generate(self):
        res = self.rule_string  # type: str
        tpl = Template('{ $$$$ = bison_callback("$name", ); }')
        for k, v in self.callback_replace.items():
            res = res.replace(k, tpl.substitute(name=v))
        return res


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
    tokens: set = None
    callback_name_set: set = None

    def __init__(self):
        self.rules = []
        self.load_rules()
        self.analysis_rules()

    def load_rules(self):
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method):
                if (reg := getattr(method, 'register', None)) and isinstance(reg, GrammarRegister):
                    self.rules.append(reg)
        return self.rules

    def analysis_rules(self):
        self.tokens = set()
        for rule in self.rules:  # type: GrammarRegister
            rule.analysis_rules()
            self.tokens.update(rule.tokens)

    def generate_rule(self):
        return "\n".join(i.generate() for i in self.rules)

    def generate(self) -> str:
        template = Template(self.trim_rules_string("""
        %{
            #include <stdio.h>
        %}
        %token $tokens

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
            tokens=" ".join(self.tokens),
            rules=self.generate_rule(),
        )




