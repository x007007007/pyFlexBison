import subprocess


class GeneratorBase(object):

    def generate(self) -> str:
        raise NotImplementedError

    def build_command(self, path):
        raise NotImplementedError

    def env_checker(self):
        raise NotImplementedError


    def run_cmd(self, cmd: list, env: dict):
        proc = subprocess.Popen(
            args=cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        return proc