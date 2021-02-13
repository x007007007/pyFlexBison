from .core_ import RunnerBNF
from .builder import Builder
import io

class PipelineMeta():

    def read_context(self, size:int ):
        raise NotImplementedError


class Pipeline(PipelineMeta):

    def __init__(self, name, lex, yacc):
        self.name = name
        self.lex = lex
        self.yacc = yacc
        self.build = Builder(self.name, self.lex, self.yacc)
        self.build.env_checker()
        self.build.clean()
        self.build.build()
        self.fp = io.StringIO("""1+2/3-4*5""")
        self.runner = RunnerBNF(name, self)

    def run(self):
        self.runner.dynamic_load()

    def read_context(self, size) -> bytes:
        return self.fp.read(size).encode("utf-8")

    def bison_proc(self, name, *args, **kwargs):
        print(f"bison_proc: {name}")
        return getattr(self.yacc, name)(*args, **kwargs)


    def token_proc(self, name, *args, **kwargs):
        print(f"token_proc: {name}")
        return getattr(self.lex, name)(*args, **kwargs)