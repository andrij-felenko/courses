ffibuilder.cdef("""
    typedef int (*comparator_t)(int, int);
    void register_callback(comparator_t cb);
    extern "Python" int py_comparator(int a, int b);
""")

# У модулі реалізації:
@ffi.def_extern()
def py_comparator(a, b):
    return (a > b) - (a < b)

lib.register_callback(lib.py_comparator)
