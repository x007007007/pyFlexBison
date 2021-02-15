"""
                  alter_database_stmt           {##}
                | alter_event_stmt              {##}
                | alter_function_stmt           {##}
                | alter_instance_stmt           {##}
                | alter_logfile_stmt            {##}
                | alter_procedure_stmt          {##}
                | alter_resource_group_stmt     {##}
                | alter_server_stmt             {##}
                | alter_tablespace_stmt         {##}
                | alter_undo_tablespace_stmt    {##}
                | alter_table_stmt              {##}
                | alter_user_stmt               {##}
                | alter_view_stmt               {##}
                | analyze_table_stmt            {##}
                | binlog_base64_event           {##}
                | drop_srs_stmt                 {##}
                | describe_stmt                 {##}
                | help                          {##}
                | drop_user_stmt                {##}
                | kill                          {##}
                | lock                          {##}
                | show_binary_logs_stmt
                | show_binlog_events_stmt
                | show_character_set_stmt
                | show_collation_stmt
                | show_columns_stmt
                | show_count_errors_stmt
                | show_count_warnings_stmt
                | show_create_database_stmt
                | show_create_event_stmt
                | show_create_function_stmt
                | show_create_procedure_stmt
                | show_create_table_stmt
                | show_create_trigger_stmt
                | show_create_user_stmt
                | show_create_view_stmt
                | show_databases_stmt
                | show_engine_logs_stmt
                | show_engine_mutex_stmt
                | show_engine_status_stmt
                | show_engines_stmt
                | show_errors_stmt
                | show_events_stmt
                | show_function_code_stmt
                | show_function_status_stmt
                | show_grants_stmt
                | show_keys_stmt
                | show_master_status_stmt
                | show_open_tables_stmt
                | show_plugins_stmt
                | show_privileges_stmt
                | show_procedure_code_stmt
                | show_procedure_status_stmt
                | show_processlist_stmt
                | show_profile_stmt
                | show_profiles_stmt
                | show_relaylog_events_stmt
                | show_replica_status_stmt
                | show_replicas_stmt
                | show_status_stmt
                | show_table_status_stmt
                | show_tables_stmt
                | show_triggers_stmt
                | show_variables_stmt
                | show_warnings_stmt
                | set_role_stmt
                | shutdown_stmt
                | signal_stmt                   {##}
                | xa                            {##}
                | unlock                        {##}
                | start_replica_stmt            {##}
                | stop_replica_stmt             {##}
                | explain_stmt                  {##}
                | create_role_stmt              {##}
                | create_srs_stmt               {##}
                | create_index_stmt             {##}
                | deallocate                    {##}
                | drop_index_stmt               {##}
                | drop_event_stmt               {##}
                | import_stmt                   {##}
                | drop_trigger_stmt             {##}
                | drop_tablespace_stmt          {##}
                | get_diagnostics               {##}
                | group_replication             {##}
                | grant                         {##}
                | keycache_stmt                 {##}
                | preload_stmt                  {##}
                | prepare                       {##}
                | purge                         {##}
                | release                       {##}
                | rename                        {##}
                | drop_role_stmt                {##}
                | drop_server_stmt              {##}
                | drop_undo_tablespace_stmt     {##}
                | drop_logfile_stmt             {##}
                | restart_server_stmt           {##}
                | repair_table_stmt             {##}
                | uninstall                     {##}
                | resignal_stmt                 {##}
                | change                        {##}


"""
from pyFlexBison.gen_bison import BisonGenerator, grammar


class SqlSimpleStmt:
    @grammar("""
        simple_statement:
                call_stmt                       {##}
                | check_table_stmt              {##}
                | checksum                      {##}
                | clone_stmt                    {##}
                | commit                        {##}
                | create                        {##}
                | create_resource_group_stmt    {##}
                | create_table_stmt             {##}
                | delete_stmt                   {##}
                | do_stmt                       {##}
                | drop_database_stmt            {##}
                | drop_function_stmt            {##}
                | drop_procedure_stmt           {##}
                | drop_resource_group_stmt      {##}
                | drop_table_stmt               {##}
                | drop_view_stmt                {##}
                | execute                       {##}
                | flush                         {##}
                | handler_stmt                  {##}
                | insert_stmt                   {##}
                | install                       {##}
                | load_stmt                     {##}
                | optimize_table_stmt           {##}
                | replace_stmt                  {##}
                | reset                         {##}
                | revoke                        {##}
                | rollback                      {##}
                | savepoint                     {##}
                | select_stmt                   {##}
                | set                           {##}
                | set_resource_group_stmt       {##}
                | start                         {##}
                | truncate_stmt                 {##}
                | update_stmt                   {##}
                | use                           {##}
                ;
    
    """, argc=1)
    def simple_statement(self, a):
        return a
