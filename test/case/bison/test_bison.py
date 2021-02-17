import os
import io
from pyFlexBison.pipeline import Pipeline
from pyFlexExample.bison.bison_lex import BisonLexGenerator
from pyFlexExample.bison.bison_parser import BisonParserGenerator
import logging

LOGGER = logging.getLogger(__name__)


def test_bison():
    with open("msyql_.yy") as fp:
        pipeline = Pipeline('test_bison_parse', BisonLexGenerator, BisonParserGenerator, fp)
        LOGGER.info(pipeline.runner)
        pipeline.run()


if __name__ == "__main__":
    print("DEBUG MODULE")
    test_bison()