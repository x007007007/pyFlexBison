import os
from pyFlexBison.pipeline import Pipeline
from pyFlexExample.calc.calc_flex import CalcFlexGenerator
from pyFlexExample.calc.calc_bison import CalcBisonGenerator


def test_dynamic_load():
    bison = CalcBisonGenerator()
    bison.env_checker()
    bison.build()

    flex = CalcFlexGenerator(bison_header=os.path.basename(bison.output_h))
    flex.env_checker()
    flex.build()

    pipeline = Pipeline('test', flex, bison)

    print(pipeline.runner)
    pipeline.run()


