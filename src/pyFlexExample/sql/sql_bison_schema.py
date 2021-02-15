from pyFlexBison.gen_bison import BisonGenerator, grammar



class SchemaGeneratorMixin:

    @grammar("""
        exists_optional:
            | IF NOT EXISTS
            | IF EXISTS
            ;
        temporary_optional:
            | TEMPORARY
            ;
        
        schema:
                CREATE SCHEMA exists_optional db_name create_schema_option
            |   CREATE DATABASE exists_optional db_name create_database_option
            |   CREATE temporary_optional TABLE exists_optional tbl_name create_table_option
            ;
        
        create_table_option:
                '(' create_definition_list ')'
            ;
        
        create_definition_list: create_definition
            | create_definition_list, create_definition
            ;
        
        create_definition:
                col_name column_definition
            | {INDEX | KEY} [index_name] [index_type] (key_part,...)
              [index_option] ...
            | {FULLTEXT | SPATIAL} [INDEX | KEY] [index_name] (key_part,...)
              [index_option] ...
            | [CONSTRAINT [symbol]] PRIMARY KEY
              [index_type] (key_part,...)
              [index_option] ...
            | [CONSTRAINT [symbol]] UNIQUE [INDEX | KEY]
              [index_name] [index_type] (key_part,...)
              [index_option] ...
            | [CONSTRAINT [symbol]] FOREIGN KEY
              [index_name] (col_name,...)
              reference_definition
            | check_constraint_definition
        

            ;
        
        
            
        opt_schema_element_list:
                /* empty */
            |	schema_element_list
            ;
        
        schema_element_list:
                schema_element
            |	schema_element_list schema_element
            ;
        
        schema_element:
                base_table_def
            |	view_def
            |	privilege_def
            ;
        
        base_table_def:
                CREATE TABLE table '(' base_table_element_commalist ')'
            ;
        
        base_table_element_commalist:
                base_table_element
            |	base_table_element_commalist ',' base_table_element
            ;
        
        base_table_element:
                column_def
            |	table_constraint_def
            ;
        
        column_def:
                column data_type column_def_opt_list
            ;
        
        column_def_opt_list:
                /* empty */
            |	column_def_opt_list column_def_opt
            ;
        
        column_def_opt:
                NOT NULLX
            |	NOT NULLX UNIQUE
            |	NOT NULLX PRIMARY KEY
            |	DEFAULT literal
            |	DEFAULT NULLX
            |	DEFAULT USER
            |	CHECK '(' search_condition ')'
            |	REFERENCES table
            |	REFERENCES table '(' column_commalist ')'
            ;
        
        table_constraint_def:
                UNIQUE '(' column_commalist ')'
            |	PRIMARY KEY '(' column_commalist ')'
            |	FOREIGN KEY '(' column_commalist ')'
                    REFERENCES table 
            |	FOREIGN KEY '(' column_commalist ')'
                    REFERENCES table '(' column_commalist ')'
            |	CHECK '(' search_condition ')'
            ;
        
        column_commalist:
                column
            |	column_commalist ',' column
            ;
        
        view_def:
                CREATE VIEW table opt_column_commalist
                AS query_spec opt_with_check_option
            ;
            
        opt_with_check_option:
                /* empty */
            |	WITH CHECK OPTION
            ;
        
        opt_column_commalist:
                /* empty */
            |	'(' column_commalist ')'
            ;
        
        privilege_def:
                GRANT privileges ON table TO grantee_commalist
                opt_with_grant_option
            ;
        
        opt_with_grant_option:
                /* empty */
            |	WITH GRANT OPTION
            ;
        
        privileges:
                ALL PRIVILEGES
            |	ALL
            |	operation_commalist
            ;
        
            
    """)
    def schema_process(self):
        pass

