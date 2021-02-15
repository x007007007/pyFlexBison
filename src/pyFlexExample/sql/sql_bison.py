from pyFlexBison.gen_bison import BisonGenerator, grammar
from .node import SQLNode

class SqlBisonGenerator(BisonGenerator):
    """
    https://github.com/wclever/NdYaccLexTool/blob/master/progs/sql2.y
    """
    @grammar("""
        sql_block_list: sql_block {##}
            |   sql_list {##}
            |   sql_block_list sql_block  {#gen_sql_block_list#}
            |   sql_block_list sql_list   {#gen_sql_block_list#}
            
        sql_block: DELIMITER_START sql_list DELIMITER_END {#gen_sql_block#}
        
        sql_list:
                sql ';'	{#gen_signal_sql#}
            |	sql_list sql ';' {#gen_sql_list#}
            ;
    """, argc=1)
    def sql_block_list(self, signal_sql):
        return [signal_sql]

    @sql_block_list.register(argc=2)
    def gen_sql_block_list(self, sql_list, sql):
        sql_list.append(sql)
        return sql_list

    @sql_block_list.register(args_list=['$1', '$2'])
    def gen_sql_block(self, delimiter, block):
        return block

    @sql_block_list.register(argc=1)
    def gen_signal_sql(self, sql):
        return sql

    @sql_block_list.register(argc=2)
    def gen_sql_list(self, sql_list, sql):
        sql_list.append(sql)
        return sql_list
