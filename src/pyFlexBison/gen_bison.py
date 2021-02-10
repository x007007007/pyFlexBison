import typing
import re
import sys
import os
import warnings
from string import Template
from .generator import CommandGeneratorBase, CodeGeneratorMixin


class GrammarRegister:
    def __init__(self, rule_string, func):
        self.__tokens = set()
        self.func = func
        self.rule_string = rule_string.strip()
        self.sub_func_map = {}

    def __repr__(self):
        rule_headers = self.rule_string.strip().split('\n', maxsplit=1)
        if len(rule_headers) > 0:
            summary = rule_headers[0]
        return f"<BNF:{summary} ...>"

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
        tpl = Template('{ $$$$ = bison_callback("$name"); }')
        for k, v in self.callback_replace.items():
            res = res.replace(k, tpl.substitute(name=v))
        return res


def grammar(rule_string):
    rule_string = CommandGeneratorBase.trim_rules_string(rule_string)
    def decorate(func):
        func.register = GrammarRegister(rule_string, func)
        return func
    return decorate


class BisonEvnCheckerMixin:
    MAC_BREW_PATH = "/usr/local/opt/bison/bin/bison"
    run_env: typing.Dict[str, str]
    bin_path: str = None
    bison_version: typing.Tuple[int, int, int] = None
    bison_bin: str = None

    def env_checker(self):
        if self.run_env is None:
            self.run_env = dict()
        if sys.platform.startswith('darwin'):
            if os.path.exists(self.MAC_BREW_PATH):
                # self.run_env['LDFLAGS'] = "-L/usr/local/opt/bison/lib"
                self.run_env['PATH'] = f"/usr/local/opt/bison/bin:{self.run_env['PATH']}"
                proc = self.run_cmd([self.MAC_BREW_PATH, '--version'], self.run_env)
                res, res_err = proc.communicate()
                res = res.decode(sys.getdefaultencoding())
                match_res = re.match(r'bison.*?\s*(\d+)\.(\d+)\.(\d+)', res)
                if match_res:
                    main, major, minor = (int(i) for i in match_res.groups())
                    self.flex_version = (main, major, minor)
                    if main < 3 or (main == 3 and major < 7 ):
                        warnings.warn(f"bison version to low: {res}", RuntimeWarning)
                    else:
                        self.bin_path = self.MAC_BREW_PATH
            else:
                raise RuntimeError("bison don't exist")
        elif sys.platform.startswith('linux'):
            pass


class BisonGenerator(BisonEvnCheckerMixin, CodeGeneratorMixin, CommandGeneratorBase):
    tokens: set = None

    def __init__(self, *args, **kwargs):
        super(BisonGenerator, self).__init__(*args, **kwargs)
        self.rules = []
        self.__load_rules()
        self.__analysis_rules()


    def __load_rules(self):
        self.rules = []
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method):
                if (reg := getattr(method, 'register', None)) and isinstance(reg, GrammarRegister):
                    self.rules.append(reg)
        return self.rules

    def __analysis_rules(self):
        self.tokens = set()
        for rule in self.rules:  # type: GrammarRegister
            rule.analysis_rules()
            self.tokens.update(rule.tokens)

    def generate_rule(self):
        rules_str = "\n".join(i.generate() for i in self.rules)
        return rules_str

    def generate(self) -> str:
        template = Template(self.trim_rules_string(r"""
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

    def get_bison_path(self):
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        return os.path.join(self.temp_dir, "bison.y")

    def build(self):
        if self.bin_path is None:
            raise RuntimeError("run env_checker first")
        bison_path = self.get_bison_path()
        self.generate_file(bison_path)
        output_c = os.path.join(self.temp_dir, 'bison.c')
        proc = self.run_cmd([
            self.bin_path,
            '-o',
            output_c,
            '-d',
            bison_path
        ], env=self.run_env)
        out, err = proc.communicate()
        if proc.returncode == 0:
            self.output_c = output_c
            self.output_h = os.path.join(self.temp_dir, 'bison.h')
        print(f"error code: {proc.returncode} \n {out.decode(sys.getdefaultencoding())} {err.decode(sys.getdefaultencoding())}")

