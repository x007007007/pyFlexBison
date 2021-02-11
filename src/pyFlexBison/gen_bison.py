import typing
import re
import sys
import os
import warnings
from string import Template
from .generator import CommandGeneratorBase, CodeGeneratorMixin


class GrammarRegister:
    def __init__(self, rule_string, func, argc: int):
        self.argc = argc
        self.__tokens = set()
        self.func = func
        self.rule_string = rule_string.strip()
        self.sub_func_map = {}
        self.sub_func_argc_map = {}

    def __repr__(self):
        rule_headers = self.rule_string.strip().split('\n', maxsplit=1)
        if len(rule_headers) > 0:
            summary = rule_headers[0]
        return f"<BNF:{summary} ...>"

    def __call__(self, argc, name=None):
        def decorate(func):
            nonlocal name
            if name is None:
                name = func.__name__
            self.sub_func_map[name] = func
            self.sub_func_argc_map[name] = argc
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
        tpl = Template('{ $$$$ = bison_callback("$name"$args); }')
        for k, v in self.callback_replace.items():
            if k == "{##}":
                argc = self.argc
            else:
                argc = self.sub_func_argc_map[k[2:-2]]
            args = [str(argc)]
            for i in range(argc):
                args.append(f"${i}")
            res = res.replace(k, tpl.substitute(
                name=v.__name__,
                args=f', {", ".join(args)}'
            ))
        return res


def grammar(rule_string, argc):
    rule_string = CommandGeneratorBase.trim_rules_string(rule_string)
    def decorate(func):
        func.register = GrammarRegister(rule_string, func, argc)
        return func
    return decorate


class BisonEvnCheckerMixin:
    MAC_BREW_PATH = "/usr/local/opt/bison/bin/bison"
    run_env: typing.Dict[str, str]
    bin_path: str = None
    bison_version: typing.Tuple[int, int, int] = None
    bison_bin: str = None
    output_c: str
    output_h: str

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

    TYPE_T_LALR = "lalr"
    TYPE_T_IELR = "ielr"
    TYPE_T_CANONICAL_LR = "canonical-lr"
    TYPE_LR_MOST = 'most'
    TYPE_LR_CONSISTENT = 'consistent'
    TYPE_LR_ACPT = 'accepting'

    def __init__(
            self,
            table_type=None,
            lr_default_reduction=None,
            *args,
            **kwargs
    ):
        self.table_type = self.TYPE_T_LALR if table_type is None else table_type
        assert self.table_type in (self.TYPE_T_LALR, self.TYPE_T_IELR, self.TYPE_T_CANONICAL_LR)
        assert lr_default_reduction in (self.TYPE_LR_ACPT, self.TYPE_LR_CONSISTENT, self.TYPE_LR_MOST, None)
        self.lr_default_reduction = lr_default_reduction
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

    def generate_optional(self):
        optionals = []
        if self.table_type:
            optionals.append(f"%define lr.type {self.table_type}")
        if self.lr_default_reduction:
            optionals.append(f"%define lr.default-reduction {self.lr_default_reduction}")

        return "\n".join(optionals)

    def generate(self) -> str:
        template = Template(self.trim_rules_string(r"""
        
        %code top {
            /* The unqualified %code or %code requires should usually 
            be more appropriate than %code top. However, occasionally 
            it is necessary to insert code much nearer the top 
            of the parser implementation file. */
            // #define _GNU_SOURCE
            // #include <stdio.h>
            #define PY_SSIZE_T_CLEAN
            #include "Python.h"
            #define YYSTYPE PyObject *
        }
        
        %code requires {
            /* 
            This is the best place to write dependency code required for 
            YYSTYPE and YYLTYPE. In other words, it’s the best place to 
            define types referenced in %union directives. If you use
             #define to override Bison’s default YYSTYPE and YYLTYPE
              definitions, then it is also the best place. However you 
              should rather %define api.value.type and api.location.type. 
            */
        }
        
        %code provides {
            /* urpose: This is the best place to write additional definitions 
            and declarations that should be provided to other modules. 
            The parser header file and the parser implementation file after 
            the Bison-generated YYSTYPE, YYLTYPE, and token definitions. */
        }
        
        %{
            int yylex();
            void yyerror(char *s);
            
            YYSTYPE bison_callback(char *name, int argc, ...) {
                printf("bison_callback %s\n", name);
            }
            
            callback_token_process(char *name, ...) {
                printf("callback_token_process %s\n", name);
            }
        %}

        
        %token $tokens
        
        $optional
        
        %%
        $rules
        %%
        
        int main(int argc, char **argv) {
            yyparse();
            return 0;
        }
        
        void yyerror(char *s) {
            fprintf(stderr, "error: %s\n", s);
        }
        """))
        return template.substitute(
            tokens=" ".join(self.tokens),
            rules=self.generate_rule(),
            optional=self.generate_optional()
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

