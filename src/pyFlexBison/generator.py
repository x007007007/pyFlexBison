import subprocess
import typing
import warnings
import os
import re

class GeneratorBase(object):

    @staticmethod
    def trim_rules_string(rule_string):
        rules = rule_string.split("\n")
        assert rules[0].strip() == "", "first line should't have rule"
        res = re.search('^ *', rules[1])
        if res:
            s, e = res.span()
            for i in range(len(rules)):
                if rules[i][:e].strip() == '':
                    rules[i] = rules[i][e:]
                else:
                    warnings.warn(f'ident not match on {i}: {rules}', SyntaxWarning)
        return "\n".join(rules)

    def build_command(self, path):
        raise NotImplementedError

    def env_checker(self):
        raise NotImplementedError

    def build(self):
        raise NotImplementedError

    def run_cmd(self, cmd: list, env: dict):
        proc = subprocess.Popen(
            args=cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        return proc


class CodeGeneratorMixin(GeneratorBase):
    def generate(self) -> str:
        raise NotImplementedError

    def generate_file(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as fp:
            fp.write(self.generate())


class CommandGeneratorBase(GeneratorBase):
    run_env: typing.Dict[str, str]
    temp_dir: str = None

    def __init__(self, envs=None, temp_dir=None, *args, **kwargs):
        self.run_env = dict(os.environ) if envs is None else envs
        self.temp_dir = './build/' if temp_dir is None else temp_dir