import os
import io
from pyFlexBison.pipeline import Pipeline
from pyFlexExample.calc.calc_flex import CalcFlexGenerator
from pyFlexExample.calc.calc_bison import CalcBisonGenerator
import logging

LOGGER = logging.getLogger(__name__)


def test_dynamic_load():
    fp = io.StringIO("""1+2/3-4*5
1 + 2 + 3 + 4
9 * 7 - 9 + 1
    """)
    bison = CalcBisonGenerator()
    bison.env_checker()
    bison.build()
    flex = CalcFlexGenerator(bison_header=os.path.basename(bison.output_h))
    flex.env_checker()
    flex.build()
    pipeline = Pipeline('test', flex, bison, fp)
    LOGGER.info(pipeline.runner)
    pipeline.run()


if __name__ == "__main__":
    print("DEBUG MODULE")
    test_dynamic_load()
