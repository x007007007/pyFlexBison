import sys
import os
from pyFlexExample.sql.sql_flex import SqlFlexGenerator
from pyFlexExample.calc.calc_flex import CalcFlexGenerator
from pyFlexBison.builder import Builder



def test_sql_flex_generate():
    sql_flex = SqlFlexGenerator()
    sql_flex.set_build_path('./build/sql_test/')
    sql_flex.env_checker()
    sql_flex.build()