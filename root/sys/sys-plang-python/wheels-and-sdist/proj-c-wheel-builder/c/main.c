#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>

/* Функція з зовнішньої бібліотеки libengine.so */
extern double compute_dot_product(const double* a, const double* b, size_t n);

static PyObject* py_dot_product(PyObject* self, PyObject* args) {
    Py_buffer buf_a;
    Py_buffer buf_b;

    if (!PyArg_ParseTuple(args, "y*y*", &buf_a, &buf_b)) {
        return NULL;
    }

    if (buf_a.len != buf_b.len || (buf_a.len % sizeof(double)) != 0) {
        PyBuffer_Release(&buf_a);
        PyBuffer_Release(&buf_b);
        PyErr_SetString(PyExc_ValueError, "Buffers must be of equal size and aligned to sizeof(double)");
        return NULL;
    }

    size_t count = (size_t)buf_a.len / sizeof(double);
    const double* ptr_a = (const double*)buf_a.buf;
    const double* ptr_b = (const double*)buf_b.buf;

    double result = compute_dot_product(ptr_a, ptr_b, count);

    PyBuffer_Release(&buf_a);
    PyBuffer_Release(&buf_b);

    return PyFloat_FromDouble(result);
}

static PyMethodDef FastMathMethods[] = {
    {"dot_product", py_dot_product, METH_VARARGS, "Compute dot product of two raw double buffers"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef fastmath_module = {
    PyModuleDef_HEAD_INIT,
    "_fastmath",
    "High performance vector math module",
    -1,
    FastMathMethods
};

PyMODINIT_FUNC PyInit__fastmath(void) {
    return PyModule_Create(&fastmath_module);
}
