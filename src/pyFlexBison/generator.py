import subprocess
import warnings
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
                    warnings.warn('ident not match on {i}', SyntaxWarning)
        return "\n".join(rules)

    def generate(self) -> str:
        raise NotImplementedError

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