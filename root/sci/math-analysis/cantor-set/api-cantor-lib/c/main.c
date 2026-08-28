#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "cantor.h"

static PyObject* py_cantor_contains(PyObject* self, PyObject* args) {
    double x;
    int depth = 30;
    if (!PyArg_ParseTuple(args, "d|i", &x, &depth)) {
        return NULL;
    }
    bool result = false;
    cantor_status_t status = cantor_contains(x, depth, &result);
    if (status != CANTOR_SUCCESS) {
        PyErr_SetString(PyExc_ValueError, "Invalid input parameters for cantor_contains");
        return NULL;
    }
    if (result) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyMethodDef CantorMethods[] = {
    {"contains", py_cantor_contains, METH_VARARGS, "Check if point x belongs to Cantor set"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cantormodule = {
    PyModuleDef_HEAD_INIT,
    "libcantor",
    "High-performance Cantor set computation module",
    -1,
    CantorMethods
};

PyMODINIT_FUNC PyInit_libcantor(void) {
    return PyModule_Create(&cantormodule);
}
