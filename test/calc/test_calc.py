import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from calc_bison import CalcBisonGenerator
from calc_flex import CalcFlexGenerator
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



