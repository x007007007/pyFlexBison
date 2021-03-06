#cython: language_level=3

cdef extern from "Python.h":
    object PyBytes_FromString(char *)
    object PyUnicode_FromString(char *)
    char *PyBytes_AsString(object o)

    object PyInt_FromLong(long ival)
    long PyInt_AsLong(object io)

    object PyList_New(int len)
    int PyList_SetItem(object list, int index, object item)

    void Py_INCREF(object o)

    object PyObject_GetAttrString(object o, char *attr_name)
    object PyTuple_New(int len)
    int PyTuple_SetItem(object p, int pos, object o)
    object PyObject_Call(object callable_object, object args, object kw)
    object PyObject_CallObject(object callable_object, object args)
    int PyObject_SetAttrString(object o, char *attr_name, object v)

cdef extern from "stdio.h":
    int printf(char *format,...)

cdef extern from "string.h":
    void *memcpy(void *dest, void *src, long n)
    int strlen(void *str)


import os
cimport dlfcn

include "print_py_obj.pyx"

cdef class RunnerBNF:
    cdef object parser
    cdef object parserHash # hash of current python parser object
    cdef object libFilename_py
    cdef object name
    cdef void *libHandler
    # rules hash str embedded in bison parser lib
    cdef char *libHash
    cdef char *libPath
    cdef object lib_path
    cdef (void)(*start_parse)(object parser)
    cdef char[10000] buffer

    def __init__(self, name, parser, lib_path):
        self.name = name
        self.parser = parser
        if not os.path.exists(lib_path):
            raise RuntimeError("{} not exist".format(lib_path))
        self.lib_path = lib_path.encode("utf-8")
        self.libPath = PyBytes_AsString(self.lib_path)

    def dynamic_load(self):
        self.libHandler = dlfcn.dlopen(self.libPath, dlfcn.RTLD_NOW|dlfcn.RTLD_GLOBAL)
        if self.libHandler == NULL:
            print(dlfcn.dlerror())
        self.start_parse =  <void (*)(object)>dlfcn.dlsym(self.libHandler, "start_parse")
        self.start_parse(self.parser)


