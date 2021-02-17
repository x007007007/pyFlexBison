import os
from pyFlexBison.pipeline import Pipeline
from pyFlexExample.sql.sql_flex import SqlFlexGenerator
from pyFlexExample.sql.sql_bison import SqlBisonGenerator


def test_sql_flex_generate():
    with open(os.path.join(os.path.dirname(__file__), 'test.sql')) as fp:
        pipeline = Pipeline("sql_test", SqlFlexGenerator, SqlBisonGenerator, fp)
        pipeline.run()