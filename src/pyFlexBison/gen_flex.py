import sys
import os
import typing
import re
from string import Template
from .generator import CommandGeneratorBase, CodeGeneratorMixin


class TokenRule():
    def __init__(self, token_r: str, token_name: str):
        assert isinstance(token_r, str)
        assert isinstance(token_name, str)
        self.token_r = token_r
        self.token_name = token_name
        self.token_process = None

    def __str__(self):
        ret_list = []
        if self.token_process is not None:
            ret_list.append(
                rf'''
                    PyObject *x = (PyObject *)callback_token_process("{self.token_process.__name__}", yytext);
                    printf("wtf: %p \n", x);
                    yylval = x + 0x10000000;
                    printf("\n callback_token_process out %p \n", yylval);
                ''')
        else:
            ret_list.append(
                rf'''
                    yylval = (PyObject *)PyUnicode_FromString(yytext);
                    Py_INCREF(yylval);
                    printf("---lex token %p\n", yylval);
                    print_py_obj(yylval);
                    printf("---lex token done%p\n", yylval);
                ''')
        if self.token_name != "":
            ret_list.append(rf"return {self.token_name};")
        return f"{self.token_r}     {'{'}  {'/* */ '.join(ret_list)}  {'}'}"

    def bind(self, method):
        self.token_process = method


class FlexEvnCheckerMixin:
    run_env: typing.Dict[str, str]
    MAC_BREW_PATH = '/usr/local/opt/flex/bin/flex'
    bin_path: str = None
    flex_version: typing.Tuple[int, int, int] = None
    flex_bin: str = None

    def env_checker(self):
        if self.run_env is None:
            self.run_env = dict()
        if sys.platform.startswith('darwin'):
            if os.path.exists(self.MAC_BREW_PATH):
                self.run_env['LDFLAGS'] = "-L/usr/local/opt/flex/lib"
                self.run_env['CPPFLAGS'] = "-I/usr/local/opt/flex/include"
                self.run_env['PATH'] = f"/usr/local/opt/flex/bin:{self.run_env['PATH']}"
                proc = self.run_cmd([self.MAC_BREW_PATH, '--version'], self.run_env)
                res, res_err = proc.communicate()
                res = res.decode(sys.getdefaultencoding())
                match_res = re.match(r'flex\s*(\d+)\.(\d+)\.(\d+)', res)
                if match_res:
                    main, major, minor = (int(i) for i in match_res.groups())
                    self.flex_version = (main, major, minor)
                    if main < 2 or (main == 2 and major < 4 ):
                        raise RuntimeError(f"Flex version to low: {res}")
                    else:
                        self.bin_path = self.MAC_BREW_PATH
            else:
                raise RuntimeError("flex don't exist")
        elif sys.platform.startswith('linux'):
            pass


class FlexGenerator(
    FlexEvnCheckerMixin,
    CodeGeneratorMixin,
    CommandGeneratorBase
):
    token_rule: str = None
    token_rule_split = '='
    ext_function: str = ''
    ext_config: str = ''

    def __init__(self, bison_header: str=None, *args, **kwargs):
        super(FlexGenerator, self).__init__(*args, **kwargs)
        self.bison_header = "bison.h" if bison_header is None else bison_header
        self.tokens = []
        self.rules = []
        if self.token_rule is not None:
            self._analysis_rule()

    def _analysis_rule(self):
        for line in self.token_rule.split("\n"):
            if line == "": continue
            sep_rule = line.split(self.token_rule_split)
            sep_rule_len = len(sep_rule)
            if sep_rule_len == 2:
                rule_string, token_name = sep_rule
                rule_string, token_name = rule_string.rstrip(), token_name.lstrip()
                rule = TokenRule(rule_string, token_name)
                if rule_method := getattr(self, f't_{token_name.lower()}', None):
                    rule.bind(rule_method)
                self.tokens.append(rule)
                self.rules.append(rule)
            elif sep_rule_len == 1:
                self.rules.append(line)
            else:
                raise SyntaxError(f"token_rule_split:{self.token_rule_split} split too much!!")

    def generate_rule(self) -> str:
        return "\n".join((str(i) for i in self.rules))

    def generate(self) -> str:
        template = Template(self.trim_rules_string(r"""
        %{    
            #include "$header_name"
            int yywrap() { return(1); }
        %}
        
        $ext_config
        
        %%
        $rules
        .       { printf("Mystery charactor %c\n", *yytext); } 
        %%
        
        $ext_function
        """))
        return template.substitute(
            rules=self.generate_rule(),
            header_name=self.bison_header,
            ext_function=self.ext_function,
            ext_config=self.ext_config,
        )

    def get_flex_path(self):
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        return os.path.join(self.temp_dir, "flex.l")

    def build(self):
        if self.bin_path is None:
            raise RuntimeError("run env_checker first")
        flex_path = self.get_flex_path()
        self.generate_file(flex_path)
        output_c = os.path.join(self.temp_dir, 'lex.yy.c')
        proc = self.run_cmd([
            self.bin_path,
            '-o',
            output_c,
            flex_path
        ], env=self.run_env)
        out, err = proc.communicate()
        if proc.returncode == 0:
            self.output_c = output_c
        else:
            print(f"error code: {proc.returncode} \n {out} {err}")
            raise RuntimeError("build failed")

