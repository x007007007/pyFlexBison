from pyFlexBison.gen_flex import FlexGenerator



class SqlFlexGenerator(FlexGenerator):
    """
    https://github.com/wclever/NdYaccLexTool/blob/master/progs/scn2.l
    """
    token_rule_split = ':=:'
    ext_function = FlexGenerator.trim_rules_string(r"""
        #ifndef MYSQL_DEFAULT_DELIMITER
         #define MYSQL_DEFAULT_DELIMITER ";"
        #endif
        char *delimiter_str = NULL;
        size_t delimiter_match_offset = 0;
        void update_delimiter_str(char * yytext) {
            if (delimiter_str != NULL) {
                free(delimiter_str);
                delimiter_str=NULL;
            }
            size_t delimiter_str_len = 0;
            size_t delimiter_men_len = (strlen(yytext) - 9) * sizeof(char) + 1;
            delimiter_str = (char*)malloc(delimiter_men_len);
            // memset(delimiter_str, '\0', delimiter_men_len);
            int yytext_len = strlen(yytext);
            int start_delimiter_str = 0;
            for(size_t i=9; i<yytext_len; i++) {
                if (start_delimiter_str == 0) {
                    if (yytext[i] == '\t' 
                       || yytext[i] == ' ') {
                        continue;
                    } else {
                        start_delimiter_str = 1;
                        delimiter_str[delimiter_str_len++] = yytext[i]
                    }
                } else {
                    if (yytext[i] == '\t' 
                       || yytext[i] == ' ') {
                        delimiter_str[delimiter_str_len] = '\0';
                        return;
                    } else {
                        start_delimiter_str = 1;
                        delimiter_str[delimiter_str_len++] = yytext[i];
                    }
                }
            }
            delimiter_str[delimiter_str_len] = '\0';
        }
        
        int delimiter_end_checker(char * yytext) {
            char *d_str = NULL;
            int d_len = 0;
            if (delimiter_str == NULL) {
                d_str = MYSQL_DEFAULT_DELIMITER;
            } else {
                d_str = delimiter_str;
            }
            d_len = strlen(d_str);

            if (yytext[0] == delimiter_str[delimiter_match_offset++]) {
                if (delimiter_match_offset > d_len) {
                    return 1;
                } eles {
                    return 0;
                }
            } else {
                delimiter_match_offset = 0;
                return -1;
            }
        }
    
    """)

    ext_config = FlexGenerator.trim_rules_string(r"""
        %s SQL
    """)
    token_rule = FlexGenerator.trim_rules_string(r"""
        DELIMITER[\t ]+.*[\t\n ]   { update_delimiter_str(yytext);}
        .              {
                            switch(delimiter_end_checker(yytext)){
                                case -1:
                                    REJECT;
                                    break;
                                case 0:
                                    yymore();
                                    break;
                                case 1:
                                    return EOF;
                                default:
                                    error("unexpect status")
                            }
                        }
        EXEC[ \t]+SQL                           { BEGIN SQL; start_save(); }
        <SQL>ALL                        :=:     ALL
        <SQL>AND                        :=:     AND
        <SQL>AVG                        :=:     AMMSC
        <SQL>MIN                        :=:     AMMSC
        <SQL>MAX                        :=:     AMMSC
        <SQL>SUM                        :=:     AMMSC
        <SQL>COUNT                      :=:     AMMSC
        <SQL>ANY                        :=:     ANY
        <SQL>AS                         :=:     AS
        <SQL>ASC                        :=:     ASC
        <SQL>AUTHORIZATION              :=:     AUTHORIZATION
        <SQL>BETWEEN                    :=:     BETWEEN
        <SQL>BY                         :=:     BY
        <SQL>CHAR(ACTER)?               :=:     CHARACTER
        <SQL>CHECK                      :=:     CHECK
        <SQL>CLOSE                      :=:     CLOSE
        <SQL>COMMIT                     :=:     COMMIT
        <SQL>CONTINUE                   :=:     CONTINUE
        <SQL>CREATE                     :=:     CREATE
        <SQL>CURRENT                    :=:     CURRENT
        <SQL>CURSOR                     :=:     CURSOR
        <SQL>DECIMAL                    :=:     DECIMAL
        <SQL>DECLARE                    :=:     DECLARE
        <SQL>DEFAULT                    :=:     DEFAULT
        <SQL>DELETE                     :=:     DELETE
        <SQL>DESC                       :=:     DESC
        <SQL>DISTINCT                   :=:     DISTINCT
        <SQL>DOUBLE                     :=:     DOUBLE
        <SQL>ESCAPE                     :=:     ESCAPE
        <SQL>EXISTS                     :=:     EXISTS
        <SQL>FETCH                      :=:     FETCH
        <SQL>FLOAT                      :=:     FLOAT
        <SQL>FOR                        :=:     FOR
        <SQL>FOREIGN                    :=:     FOREIGN
        <SQL>FOUND                      :=:     FOUND
        <SQL>FROM                       :=:     FROM
        <SQL>GO[ \t]*TO                 :=:     GOTO
        <SQL>GRANT                      :=:     GRANT
        <SQL>GROUP                      :=:     GROUP
        <SQL>HAVING                     :=:     HAVING
        <SQL>IN                         :=:     IN
        <SQL>INDICATOR                  :=:     INDICATOR
        <SQL>INSERT                     :=:     INSERT
        <SQL>INT(EGER)?                 :=:     INTEGER
        <SQL>INTO                       :=:     INTO
        <SQL>IS                         :=:     IS
        <SQL>KEY                        :=:     KEY
        <SQL>LANGUAGE                   :=:     LANGUAGE
        <SQL>LIKE                       :=:     LIKE
        <SQL>NOT                        :=:     NOT
        <SQL>NULL                       :=:     NULLX
        <SQL>NUMERIC                    :=:     NUMERIC
        <SQL>OF                         :=:     OF
        <SQL>ON                         :=:     ON
        <SQL>OPEN                       :=:     OPEN
        <SQL>OPTION                     :=:     OPTION
        <SQL>OR                         :=:     OR
        <SQL>ORDER                      :=:     ORDER
        <SQL>PRECISION                  :=:     PRECISION
        <SQL>PRIMARY                    :=:     PRIMARY
        <SQL>PRIVILEGES                 :=:     PRIVILEGES
        <SQL>PROCEDURE                  :=:     PROCEDURE
        <SQL>PUBLIC                     :=:     PUBLIC
        <SQL>REAL                       :=:     REAL
        <SQL>REFERENCES                 :=:     REFERENCES
        <SQL>ROLLBACK                   :=:     ROLLBACK
        <SQL>SCHEMA                     :=:     SCHEMA
        <SQL>SELECT                     :=:     SELECT
        <SQL>SET                        :=:     SET
        <SQL>SMALLINT                   :=:     SMALLINT
        <SQL>SOME                       :=:     SOME
        <SQL>SQLCODE                    :=:     SQLCODE
        <SQL>TABLE                      :=:     TABLE
        <SQL>TO                         :=:     TO
        <SQL>UNION                      :=:     UNION
        <SQL>UNIQUE                     :=:     UNIQUE
        <SQL>UPDATE                     :=:     UPDATE
        <SQL>USER                       :=:     USER
        <SQL>VALUES                     :=:     VALUES
        <SQL>VIEW                       :=:     VIEW
        <SQL>WHENEVER                   :=:     WHENEVER
        <SQL>WHERE                      :=:     WHERE
        <SQL>WITH                       :=:     WITH
        <SQL>WORK                       :=:     WORK
        
            /* punctuation */
        
        <SQL>"="    |
        <SQL>"<>"   |
        <SQL>"<"    |
        <SQL>">"    |
        <SQL>"<="   |
        <SQL>">="                       :=: COMPARISON
        
        <SQL>[-+*/(),.;]                :=: yytext[0]
        
            /* names */
        <SQL>[A-Za-z][A-Za-z0-9_]*      :=: NAME
        
            /* parameters */
        <SQL>":"[A-Za-z][A-Za-z0-9_]*    {
                    save_param(yytext+1);
                    return PARAMETER;
                }
        
            /* numbers */
        
        <SQL>[0-9]+             |
        <SQL>[0-9]+"."[0-9]*    |
        <SQL>"."[0-9]*                                      :=:     INTNUM
        
        <SQL>[0-9]+[eE][+-]?[0-9]+    |
        <SQL>[0-9]+"."[0-9]*[eE][+-]?[0-9]+ |
        <SQL>"."[0-9]*[eE][+-]?[0-9]+                       :=:     APPROXNUM
        
            /* strings */
        
        <SQL>'[^'\n]*'    {
                int c = input();
        
                unput(c);    /* just peeking */
                if(c != '\'') {
                    SV;return STRING;
                } else
                    yymore();
            }
                
        <SQL>'[^'\n]*$                          { yyerror("Unterminated string"); }
        
        <SQL>\n                                 { save_str(" ");lineno++; }
        \n                                      { lineno++; ECHO; }
        
        <SQL>[ \t\r]+                           save_str(" ");    /* white space */
        
        <SQL>"--".*                             ;            /* comment */
        
        .                                   ECHO;            /* random non-SQL text */
    """)

    def t_number(self, token: str) -> int:
        return int(token)

