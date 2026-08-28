#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

/**
 * Імпортує модуль math та викликає функцію sqrt засобами чистого C C-API.
 */
int calculate_square_root_c(double value, double *result) {
    // 1. Імпортуємо системний модуль (повертає New reference)
    PyObject *math_mod = PyImport_ImportModule("math");
    if (!math_mod) {
        PyErr_Print();
        return -1;
    }

    // 2. Отримуємо функцію sqrt зі словника модуля
    PyObject *sqrt_func = PyObject_GetAttrString(math_mod, "sqrt");
    Py_DECREF(math_mod); // Модуль більше не потрібен напряму

    if (!sqrt_func || !PyCallable_Check(sqrt_func)) {
        Py_XDECREF(sqrt_func);
        PyErr_Print();
        return -1;
    }

    // 3. Викликаємо функцію з числовим аргументом
    PyObject *args = PyTuple_Pack(1, PyFloat_FromDouble(value));
    PyObject *py_res = PyObject_CallObject(sqrt_func, args);
    Py_DECREF(sqrt_func);
    Py_DECREF(args);

    if (!py_res) {
        PyErr_Print();
        return -1;
    }

    *result = PyFloat_AsDouble(py_res);
    Py_DECREF(py_res);
    return 0;
}
