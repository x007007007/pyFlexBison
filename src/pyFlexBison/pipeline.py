import os
import logging
from pyFlexBison.libcore_ import RunnerBNF
from .builder import Builder
from .gen_bison import BisonGenerator
from .gen_flex import FlexGenerator

LOGGER = logging.getLogger(__name__)


class PipelineMeta():

    def read_context(self, size:int ):
        raise NotImplementedError


class Pipeline(PipelineMeta):
    lex: FlexGenerator
    yacc: BisonGenerator
    def __init__(self, name, lex_cls, yacc_cls, fp, lex_kwargs=None, yacc_kwargs=None):
        assert issubclass(lex_cls, FlexGenerator)
        assert issubclass(yacc_cls, BisonGenerator)
        self.name = name
        self.build_folder = f"./build/{name}/"
        self.lex_kwargs = lex_kwargs or {}
        self.yacc_kwargs = yacc_kwargs or {}
        self.yacc = yacc_cls(**self.yacc_kwargs)
        self.yacc.env_checker()
        self.yacc.set_build_path(self.build_folder)
        self.yacc.build()
        self.lex = lex_cls(bison_header=os.path.basename(self.yacc.output_h))
        self.lex.env_checker()
        self.lex.set_build_path(self.build_folder)
        self.lex.build()

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

    def on_process_done(self):

        print("on_process_done")