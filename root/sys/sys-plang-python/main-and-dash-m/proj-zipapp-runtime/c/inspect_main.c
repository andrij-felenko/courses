/* inspect_main.c — Інспекція стану __main__ після завантаження */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

void inspect_main_module(void) {
    /* Отримуємо вказівник на завантажений модуль __main__ */
    PyObject* main_mod = PyImport_AddModule("__main__");
    if (!main_mod) {
        PyErr_Print();
        return;
    }

    PyObject* main_dict = PyModule_GetDict(main_mod); /* Запозичене посилання */

    /* Зчитуємо системні атрибути __file__ та __loader__ */
    PyObject* py_file = PyDict_GetItemString(main_dict, "__file__");
    PyObject* py_spec = PyDict_GetItemString(main_dict, "__spec__");

    if (py_file) {
        PyObject* str_repr = PyObject_Str(py_file);
        const char* file_str = PyUnicode_AsUTF8(str_repr);
        printf("[C Debug] __main__.__file__ = %s\n", file_str);
        Py_XDECREF(str_repr);
    }

    if (py_spec && py_spec != Py_None) {
        PyObject* spec_name = PyObject_GetAttrString(py_spec, "name");
        if (spec_name) {
            printf("[C Debug] __main__.__spec__.name = %s\n", PyUnicode_AsUTF8(spec_name));
            Py_DECREF(spec_name);
        }
    }
}
