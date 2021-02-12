import sys
import os
from pyFlexExample.calc.calc_bison import CalcBisonGenerator
from pyFlexExample.calc.calc_flex import CalcFlexGenerator
from pyFlexBison.builder import Builder


def test_builder_pipeline():
    bison = CalcBisonGenerator()
    bison.env_checker()
    bison.build()

    flex = CalcFlexGenerator(bison_header=os.path.basename(bison.output_h))
    flex.env_checker()
    flex.build()

    builder = Builder("calc", flex, bison)
    builder.env_checker()
    builder.build()



