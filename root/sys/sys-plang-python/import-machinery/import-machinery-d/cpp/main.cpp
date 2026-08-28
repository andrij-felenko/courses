#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string_view>

// RAII-обгортка над PyObject* для безпечного автоматичного зменшення посилань
struct PyDeleter {
    void operator()(PyObject* ptr) const noexcept {
        if (ptr) {
            Py_DECREF(ptr);
        }
    }
};

using ScopedPyObject = std::unique_ptr<PyObject, PyDeleter>;

/**
 * Ідіоматичний C++20 клас для імпорту та взаємодії з модулями CPython.
 */
class PythonImporter {
public:
    static double calculate_sqrt(double value) {
        // 1. Імпорт модуля через RAII
        ScopedPyObject math_mod(PyImport_ImportModule("math"));
        if (!math_mod) {
            throw std::runtime_error("Не вдалося імпортувати модуль math");
        }

        // 2. Отримання атрибута функції
        ScopedPyObject sqrt_func(PyObject_GetAttrString(math_mod.get(), "sqrt"));
        if (!sqrt_func || !PyCallable_Check(sqrt_func.get())) {
            throw std::runtime_error("Функція sqrt відсутня або не є викликаємою");
        }

        // 3. Підготовка аргументів та виклик
        ScopedPyObject arg(PyFloat_FromDouble(value));
        ScopedPyObject args_tuple(PyTuple_Pack(1, arg.get()));
        ScopedPyObject py_result(PyObject_CallObject(sqrt_func.get(), args_tuple.get()));

        if (!py_result) {
            throw std::runtime_error("Помилка виконання функції math.sqrt");
        }

        return PyFloat_AsDouble(py_result.get());
    }
};
