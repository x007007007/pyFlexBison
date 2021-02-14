import logging

from .core_ import RunnerBNF
from .builder import Builder

LOGGER = logging.getLogger(__name__)


class PipelineMeta():

    def read_context(self, size:int ):
        raise NotImplementedError


class Pipeline(PipelineMeta):

    def __init__(self, name, lex, yacc, fp):
        self.name = name
        self.lex = lex
        self.yacc = yacc
        self.build = Builder(self.name, self.lex, self.yacc)
        self.build.env_checker()
        self.build.clean()
        self.build.build()
        self.fp = fp
        self.runner = RunnerBNF(name, self)

    def run(self):
        self.runner.dynamic_load()

    def read_context(self, size) -> bytes:
        return self.fp.read(size).encode("utf-8")

    def bison_proc(self, name, *args, **kwargs):
        LOGGER.info(f"python print {name} {args}, {kwargs}")
        res = getattr(self.yacc, name)(*args, **kwargs)
        return res

    def token_proc(self, name, *args, **kwargs):
        LOGGER.info(f"python print {name} {args}, {kwargs}")
        res = getattr(self.lex, name)(*args, **kwargs)

        return res