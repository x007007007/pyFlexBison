import typing
import re
import sys
import os
import warnings
from string import Template
from .generator import CommandGeneratorBase, CodeGeneratorMixin


class GrammarRegister:
    def __init__(self, rule_string, func, argc: int=None, args_list:list=None):
        self.argc = argc
        self.args_list = args_list
        self.__tokens = set()
        self.func = func
        self.rule_string = rule_string.strip()
        self.sub_func_map = {}
        self.sub_func_argc_map = {}
        self.sub_func_argv_list_map = {}

    def __repr__(self):
        rule_headers = self.rule_string.strip().split('\n', maxsplit=1)
        if len(rule_headers) > 0:
            summary = rule_headers[0]
        return f"<BNF:{summary} ...>"

    def __call__(self, argc=None, args_list=None, name=None):
        def decorate(func):
            nonlocal name
            if name is None:
                name = func.__name__
            self.sub_func_map[name] = func
            self.sub_func_argc_map[name] = argc
            self.sub_func_argv_list_map[name] = args_list
            return func
        return decorate

    @property
    def tokens(self):
        return self.__tokens

    def analysis_rules(self):
        self.callback_name_set = set()
        res = re.findall(r"(?<=\s)([A-Z_]+)(?:\s)", self.rule_string, re.M | re.S)
        self.__tokens = set(res)
        self.callback_replace = dict()
        for name_replace_hold in re.findall(r"{#\w*?#}", self.rule_string, re.M | re.S):
            callback_name = name_replace_hold[2:-2]
            if callback_name == '':
                callback_method = self.func
            else:
                callback_method = self.sub_func_map.get(callback_name, None)
            if not callback_method:
                raise SyntaxError(f"requirement a not exist callback: {callback_name}")
            else:
                self.callback_replace[name_replace_hold] = callback_method

    def get_argv_str(self, k, v):

        if k == "{##}":
            argc = self.argc
            args_list = self.args_list
        else:
            argc = self.sub_func_argc_map.get(k[2:-2])
            args_list = self.sub_func_argv_list_map.get(k[2:-2])
        if args_list is None:
            args_list = [f"${i + 1}" for i in range(argc)]
        elif argc is None:
            argc = len(args_list)
        else:
            raise SyntaxError("argc or argv at should set one")
        args = [str(argc)]
        args.extend(args_list)
        print(args)
        return f', {", ".join(args)}'

    def generate(self):
        res = self.rule_string  # type: str
        tpl = Template('{ $$$$ = bison_callback("$name"$args); }')
        for k, v in self.callback_replace.items():
            res = res.replace(k, tpl.substitute(
                name=v.__name__,
                args=self.get_argv_str(k, v)
            ))
        return res


def grammar(rule_string, argc=None, args_list=None):
    rule_string = CommandGeneratorBase.trim_rules_string(rule_string)
    def decorate(func):
        func.register = GrammarRegister(rule_string, func, argc, args_list)
        return func
    return decorate


class BisonEvnCheckerMixin:
    MAC_BREW_PATH = "/usr/local/opt/bison/bin/bison"
    run_env: typing.Dict[str, str]
    bin_path: str = None
    bison_version: typing.Tuple[int, int, int] = None
    bison_bin: str = None
    output_c: str
    output_h: str

    def env_checker(self):
        if self.run_env is None:
            self.run_env = dict()
        if sys.platform.startswith('darwin'):
            if os.path.exists(self.MAC_BREW_PATH):
                # self.run_env['LDFLAGS'] = "-L/usr/local/opt/bison/lib"
                self.run_env['PATH'] = f"/usr/local/opt/bison/bin:{self.run_env['PATH']}"
                proc = self.run_cmd([self.MAC_BREW_PATH, '--version'], self.run_env)
                res, res_err = proc.communicate()
                res = res.decode(sys.getdefaultencoding())
                match_res = re.match(r'bison.*?\s*(\d+)\.(\d+)\.(\d+)', res)
                if match_res:
                    main, major, minor = (int(i) for i in match_res.groups())
                    self.flex_version = (main, major, minor)
                    if main < 3 or (main == 3 and major < 7 ):
                        warnings.warn(f"bison version to low: {res}", RuntimeWarning)
                    else:
                        self.bin_path = self.MAC_BREW_PATH
            else:
                raise RuntimeError("bison don't exist")
        elif sys.platform.startswith('linux'):
            pass


class BisonGenerator(BisonEvnCheckerMixin, CodeGeneratorMixin, CommandGeneratorBase):
    tokens: set = None

    TYPE_T_LALR = "lalr"
    TYPE_T_IELR = "ielr"
    TYPE_T_CANONICAL_LR = "canonical-lr"
    TYPE_LR_MOST = 'most'
    TYPE_LR_CONSISTENT = 'consistent'
    TYPE_LR_ACPT = 'accepting'

    def __init__(
            self,
            table_type=None,
            lr_default_reduction=None,
            *args,
            **kwargs
    ):
        self.table_type = self.TYPE_T_LALR if table_type is None else table_type
        assert self.table_type in (self.TYPE_T_LALR, self.TYPE_T_IELR, self.TYPE_T_CANONICAL_LR)
        assert lr_default_reduction in (self.TYPE_LR_ACPT, self.TYPE_LR_CONSISTENT, self.TYPE_LR_MOST, None)
        self.lr_default_reduction = lr_default_reduction
        super(BisonGenerator, self).__init__(*args, **kwargs)
        self.rules = []
        self.__load_rules()
        self.__analysis_rules()

    def __load_rules(self):
        self.rules = []
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method):
                if (reg := getattr(method, 'register', None)) and isinstance(reg, GrammarRegister):
                    self.rules.append(reg)
        return self.rules

    def __analysis_rules(self):
        self.tokens = set()
        for rule in self.rules:  # type: GrammarRegister
            rule.analysis_rules()
            self.tokens.update(rule.tokens)
        self.tokens_list = list(self.tokens)
        self.tokens_list.sort()

    def generate_rule(self):
        rules_str = "\n".join(i.generate() for i in self.rules)
        return rules_str

    def generate_optional(self):
        optionals = []
        if self.table_type:
            optionals.append(f"%define lr.type {self.table_type}")
        if self.lr_default_reduction:
            optionals.append(f"%define lr.default-reduction {self.lr_default_reduction}")

        return "\n".join(optionals)

    def generate(self) -> str:
        template = Template(self.trim_rules_string(r"""
        
        %code top {
            /* The unqualified %code or %code requires should usually 
            be more appropriate than %code top. However, occasionally 
            it is necessary to insert code much nearer the top 
            of the parser implementation file. */
            #include <stdio.h>
            #include <stdarg.h>
            #define PY_SSIZE_T_CLEAN
            #include "Python.h"
            #define YYSTYPE PyObject *
            extern void print_py_obj(PyObject *);
        }
        
        %code requires {
            /* 
            This is the best place to write dependency code required for 
            YYSTYPE and YYLTYPE. In other words, it’s the best place to 
            define types referenced in %union directives. If you use
             #define to override Bison’s default YYSTYPE and YYLTYPE
              definitions, then it is also the best place. However you 
              should rather %define api.value.type and api.location.type. 
            */
            #define PY_SSIZE_T_CLEAN
            #include "Python.h"
            #define YYSTYPE PyObject *
            
            
            
            int yy_from_python_input(PyObject * pipeline, char * buf,int * result_len, int max_size);
            
            PyObject *py_pipeline;
            #define YY_INPUT(buf, result, max_size) { \
                yy_from_python_input(py_pipeline, buf, &result, max_size); \
            }
        }
        
        %code provides {
            /* urpose: This is the best place to write additional definitions 
            and declarations that should be provided to other modules. 
            The parser header file and the parser implementation file after 
            the Bison-generated YYSTYPE, YYLTYPE, and token definitions. */
        }
        
        %{
            int yylex();
            void yyerror(char *s);
            PyObject 
                *py_pipeline = NULL,
                *bison_proc_cb = NULL,
                *token_proc_cb = NULL,
                *read_callback = NULL;
            
            YYSTYPE bison_callback(char *name, int argc, ...) {
                va_list ap;
                PyObject 
                    *args = NULL,
                    *temp = NULL,
                    *handle = NULL,
                    *kwargs = NULL,
                    *result = NULL;
                // printf("entry bison_callback %s \n", name);
                
                args = PyTuple_New(argc + 1);
                if(args == NULL) {
                    // printf("Py_BuildValue Error \n");
                    goto error_defer_0;
                } else {
                    Py_INCREF(args);
                    handle =  PyUnicode_FromString(name);
                    Py_INCREF(handle);
                    PyTuple_SET_ITEM(args, 0, handle);
                    // printf("263 %p  %d\n", handle, argc);
                    
                    // -----------------------------------------------
                    va_start(ap, argc);
                    for(int i = 0; i < argc; i++) {
                        handle = (PyObject *)va_arg(ap, PyObject *);
                        if(handle == NULL){
                            handle = Py_None;
                        }
                        // printf("va_push %d : %p\n", i + 1, handle);
                        Py_INCREF(handle);
                        // print_py_obj(handle);
                        PyTuple_SET_ITEM(args, i + 1, handle);
                    }
                    va_end(ap);
                    // print_py_obj(args);
                    // ------------------------------------------------
                    // printf("273 bison_callback %s\n", name);
                    if(bison_proc_cb == NULL) {
                        // printf("Error bison_proc is NULL\n");
                        // print_py_obj(py_pipeline);
                        goto error_defer_1;
                    }
                    kwargs = PyDict_New();
                    if (kwargs == NULL) {
                        // printf("kwargs allow failed\n");
                        goto error_defer_2;
                    } else {
                        Py_INCREF(kwargs);
                        // print_py_obj(args);
                        // print_py_obj(kwargs);
                        result = PyObject_Call(bison_proc_cb, args, kwargs);
                        if(result == NULL) {
                            goto error_defer_2;
                        } else {
                            Py_INCREF(result);
                            Py_DECREF(args);
                            Py_DECREF(kwargs);
                            // printf("--{bison_callback ret result addr: %p\n", result);
                            // print_py_obj(result);
                            // printf("--}%p\n", result);
                            return result;           
                        }
                    }
                }
                error_defer_2:
                    Py_DECREF(kwargs);
                error_defer_1:
                    Py_DECREF(args);
                error_defer_0:
                    printf("bison error occur\n!");
                    Py_INCREF(Py_None);
                    return Py_None;
            }
            
            PyObject* callback_token_process(char *name, char *match_token) {
                printf("callback_token_process %s: (%s)\n", name, match_token);
                PyObject 
                    *result = NULL,
                    *args = NULL,
                    *kwargs = NULL;
                                    
                if (name == NULL || match_token == NULL){
                    printf("name or match token not exist \n");
                    goto error_defer_4;
                }
                args = Py_BuildValue("(ss)", name, match_token); 
                if(args == NULL){ 
                    goto error_defer_4;
                }
                Py_INCREF(args);
                kwargs = PyDict_New();
                if(args == NULL){ 
                    goto error_defer_3;
                }
                Py_INCREF(kwargs);
                if(token_proc_cb == NULL) {
                    goto error_defer_2;
                }
                result = PyObject_Call(token_proc_cb, args, kwargs);
                if (result == NULL) {
                    printf("run token proc failed: args & kwargs===========\n");
                    PyErr_Print();
                    print_py_obj(args);
                    print_py_obj(kwargs);
                    printf("run token proc failed done===========\n");
                    goto error_defer_1;
                } else {
                    Py_INCREF(result);
                    Py_DECREF(kwargs);
                    Py_DECREF(args);
                    printf("yylex result p: %p \n", result);
                    return result;
                }
                assert("never shouldn't running to here\n");
                
                error_defer_1:
                error_defer_2:
                    Py_DECREF(kwargs);
                error_defer_3:
                    Py_DECREF(args);
                error_defer_4:
                    printf("token parse error occur \n");
                    Py_INCREF(Py_None);
                    result = Py_None;
                    return result;
            }
            
            int yy_from_python_input(PyObject *py_pipeline, char *buf, int *read_number, int max_size) {
                printf("wait input %p\n", py_pipeline);
                
                if(read_callback == NULL) {
                    // error
                    printf("read_callback is NULL");
                    *read_number = 0;
                    return 0;
                }
                PyObject *args = Py_BuildValue("(i)", max_size);  
                if(args == NULL) {
                    printf("Py_BuildValue Error ");
                    return 0;
                    //error
                } else {
                    Py_INCREF(args);
                    PyObject *kwargs = PyDict_New();
                    if (kwargs == NULL) {
                        //error
                        return 0;
                    } else {
                        Py_INCREF(kwargs);
                        PyObject *result = PyObject_Call(read_callback, args, kwargs);
                        if(result == NULL) {
                            // error
                            return 0;
                        } else {
                            char *py_char = PyBytes_AsString(result);
                            int py_char_len = strlen(py_char);
                            *read_number = py_char_len;
                            memcpy(buf, py_char, py_char_len);
                            // printf("read from python: %s\n", py_char);
                            Py_DECREF(result);
                        }
                        Py_DECREF(kwargs);    
                    }
                    Py_DECREF(args);
                }
                return *read_number;
            }
        %}

        
        %token $tokens
        
        $optional
        
        %%
        $rules
        %%
        
        // __attribute__ ((dllexport))
        int start_parse(
            PyObject *_pipeline,
            ...
        ) {
            py_pipeline = _pipeline;
            // PyObject *done_callback = PyObject_GetAttrString(py_pipeline, "done");
            bison_proc_cb = PyObject_GetAttrString(py_pipeline, "bison_proc");
            token_proc_cb = PyObject_GetAttrString(py_pipeline, "token_proc");
            read_callback = PyObject_GetAttrString(py_pipeline, "read_context");
            Py_INCREF(bison_proc_cb);
            Py_INCREF(token_proc_cb);
            Py_INCREF(read_callback);
            // Py_INCREF(done_callback);
            print_py_obj(bison_proc_cb);
            print_py_obj(token_proc_cb);
            print_py_obj(read_callback);
            yyparse();
                // if (done_callback != NULL) {
                //     PyObject *args = PyTuple_New(0);
                //     PyObject *kwargs = PyDict_New();
                //     Py_INCREF(args); Py_INCREF(kwargs);
                //     PyObject_Call(done_callback, args, kwargs);
                //     Py_DECREF(args); Py_DECREF(kwargs);
                // }
            Py_DECREF(bison_proc_cb);
            Py_DECREF(token_proc_cb);
            Py_DECREF(read_callback);
            // Py_DECREF(done_callback);
            return 0;
        }
        
        void yyerror(char *s) {
            fprintf(stderr, "error!!!!!: %s\n", s);
        }
        """))
        return template.substitute(
            tokens=" ".join(self.tokens_list),
            rules=self.generate_rule(),
            optional=self.generate_optional()
        )

    def get_bison_path(self):
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
        return os.path.join(self.temp_dir, "bison.y")

    def build(self):
        if self.bin_path is None:
            raise RuntimeError("run env_checker first")
        bison_path = self.get_bison_path()
        self.generate_file(bison_path)
        output_c = os.path.join(self.temp_dir, 'bison.c')
        proc = self.run_cmd([
            self.bin_path,
            '-o',
            output_c,
            '-d',
            bison_path
        ], env=self.run_env)
        out, err = proc.communicate()
        if proc.returncode == 0:
            self.output_c = output_c
            self.output_h = os.path.join(self.temp_dir, 'bison.h')
        # print(f"error code: {proc.returncode} \n {out.decode(sys.getdefaultencoding())} {err.decode(sys.getdefaultencoding())}")

