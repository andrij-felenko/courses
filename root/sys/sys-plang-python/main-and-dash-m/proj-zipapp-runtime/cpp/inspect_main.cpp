// inspect_main.cpp — Інспекція стану __main__ мовою C++
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string_view>

void inspect_main_module_cpp() {
    PyObject* main_mod = PyImport_AddModule("__main__");
    if (!main_mod) {
        PyErr_Print();
        return;
    }

    PyObject* main_dict = PyModule_GetDict(main_mod);

    auto print_attr = [main_dict](const char* attr_name) {
        PyObject* val = PyDict_GetItemString(main_dict, attr_name);
        if (val && val != Py_None) {
            PyObject* repr = PyObject_Str(val);
            std::cout << "[C++ Debug] __main__." << attr_name << " = " 
                      << PyUnicode_AsUTF8(repr) << std::endl;
            Py_XDECREF(repr);
        }
    };

    print_attr("__file__");
    print_attr("__package__");
    print_attr("__doc__");
}
