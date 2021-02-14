#cython: language_level=3

cimport cpython as cpy
from libc cimport stdio

cdef public void print_py_obj(object obj):
    cdef char *obj_repr_c_str
    cpy.Py_INCREF(obj)
    obj_repr = cpy.PyObject_Repr(obj)
    if obj_repr:
        cpy.Py_INCREF(obj_repr)
        temp_bytes = cpy.PyUnicode_AsEncodedString(obj_repr, "UTF-8", "strict")
        if (temp_bytes):
            cpy.Py_INCREF(temp_bytes)
            obj_repr_c_str = cpy.PyBytes_AS_STRING(temp_bytes)
            stdio.printf("py obj: %s\n", obj_repr_c_str)
            cpy.Py_DECREF(temp_bytes)
        else:
            pass
        cpy.Py_DECREF(obj_repr)
    cpy.Py_DECREF(obj)

