#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <span>
#include <vector>
#include <memory>
#include <string_view>

/* Функція з зовнішньої бібліотеки libengine.so */
extern "C" double compute_dot_product(const double* a, const double* b, size_t n);

namespace fastmath {

class PyBufferGuard {
public:
    explicit PyBufferGuard(Py_buffer& buf) noexcept : buf_(buf) {}
    ~PyBufferGuard() noexcept { PyBuffer_Release(&buf_); }
    PyBufferGuard(const PyBufferGuard&) = delete;
    PyBufferGuard& operator=(const PyBufferGuard&) = delete;

private:
    Py_buffer& buf_;
};

static PyObject* dot_product(PyObject* /* self */, PyObject* args) {
    Py_buffer raw_a{};
    Py_buffer raw_b{};

    if (!PyArg_ParseTuple(args, "y*y*", &raw_a, &raw_b)) {
        return nullptr;
    }

    PyBufferGuard guard_a(raw_a);
    PyBufferGuard guard_b(raw_b);

    if (raw_a.len != raw_b.len || (raw_a.len % sizeof(double)) != 0) {
        PyErr_SetString(PyExc_ValueError, "Buffers must be of equal size and aligned to sizeof(double)");
        return nullptr;
    }

    const size_t count = static_cast<size_t>(raw_a.len) / sizeof(double);
    std::span<const double> span_a(static_cast<const double*>(raw_a.buf), count);
    std::span<const double> span_b(static_cast<const double*>(raw_b.buf), count);

    double result = compute_dot_product(span_a.data(), span_b.data(), span_a.size());
    return PyFloat_FromDouble(result);
}

} // namespace fastmath

static PyMethodDef FastMathMethods[] = {
    {"dot_product", fastmath::dot_product, METH_VARARGS, "Compute dot product of two raw double buffers"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef fastmath_module = {
    PyModuleDef_HEAD_INIT,
    "_fastmath",
    "High performance vector math module (C++ backend)",
    -1,
    FastMathMethods
};

extern "C" PyMODINIT_FUNC PyInit__fastmath(void) {
    return PyModule_Create(&fastmath_module);
}
