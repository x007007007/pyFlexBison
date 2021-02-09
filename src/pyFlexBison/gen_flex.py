import sys
import os
import typing
import re
from string import Template
from .generator import GeneratorBase


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
            ret_list.append(f'callback_token_process("{self.token_process.__name__}");')
        if self.token_name != "":
            ret_list.append(f"return {self.token_name};")
        return f"{self.token_r}     {'{'}  {'/* */ '.join(ret_list)}  {'}'}"

    def bind(self, method):
        self.token_process = method


class FlexGenerator(GeneratorBase):
    MAC_BREW_PATH = '/usr/local/opt/flex/bin/flex'
    bin_path: str = None
    flex_version: typing.Tuple[int, int, int] = None
    flex_bin: str = None
    token_rule: str = None
    run_env: typing.Dict[str, str]

    def __init__(self, bison_header: str=None, envs=None):
        if bison_header is None:
            self.bison_header = "flex_bison.h"
        self.temp_dir = "./build/"
        if envs is None:
            self.run_env = dict(os.environ)
        else:
            self.run_env = envs
        self.tokens = []
        if self.token_rule is not None:
            self._analysis_rule()

    def _analysis_rule(self):
        for line in self.token_rule.split("\n"):
            if (line := line.strip()) == "": continue
            rule_string, token_name = line.split("=")
            rule_string, token_name = rule_string.strip(), token_name.strip()
            rule = TokenRule(rule_string, token_name)
            if rule_method := getattr(self, f't_{token_name.lower()}', None):
                rule.bind(rule_method)
            self.tokens.append(rule)

    def generate_rule(self) -> str:
        return "\n".join((str(i) for i in self.tokens))

    def env_checker(self):
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

    def generate(self) -> str:
        template = Template(self.trim_rules_string("""
        %{
            #include "$header_name"
        %}
        
        %%
        $rules
        %%
        """))
        return template.substitute(
            rules=self.generate_rule(),
            header_name=self.bison_header
        )

    def get_flex_path(self):
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        return os.path.join(self.temp_dir, "flex.l")

    def generate_file(self, flex_path):
        with open(flex_path, 'w', encoding='utf-8') as fp:
            fp.write(self.generate())


    def build(self):
        if self.bin_path is None:
            raise RuntimeError("run env_checker first")
        flex_path = self.get_flex_path()
        self.generate_file(flex_path)
        proc = self.run_cmd([
            self.bin_path,
            '-o',
            os.path.join(self.temp_dir, 'lex.yy.c'),
            flex_path
        ], env=self.run_env)
        out, err = proc.communicate()
        print(f"error code: {proc.returncode} \n {out} {err}")
