#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string_view>
#include <memory>
#include <stdexcept>

/* RAII-обгортка над життєвим циклом вбудованого інтерпретатора CPython */
class PythonRuntime {
public:
    explicit PythonRuntime(std::wstring_view venv_path) {
        PyConfig config;
        PyConfig_InitPythonConfig(&config);

        PyStatus status = PyConfig_SetString(&config, &config.prefix, venv_path.data());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося встановити prefix для PyConfig");
        }

        config.site_import = 1;

        status = Py_InitializeFromConfig(&config);
        PyConfig_Clear(&config);
        if (PyStatus_Exception(status)) {
            throw std::runtime_error("Помилка ініціалізації CPython із PyConfig");
        }
    }

    ~PythonRuntime() {
        if (Py_IsInitialized()) {
            Py_FinalizeEx();
        }
    }

    PythonRuntime(const PythonRuntime&) = delete;
    PythonRuntime& operator=(const PythonRuntime&) = delete;

    void inspect_prefixes() const {
        PyObject* sys_mod = PyImport_ImportModule("sys");
        if (!sys_mod) {
            PyErr_Print();
            throw std::runtime_error("Не вдалося імпортувати модуль sys");
        }

        auto py_decref = [](PyObject* obj) { Py_XDECREF(obj); };
        std::unique_ptr<PyObject, decltype(py_decref)> sys_guard(sys_mod, py_decref);

        PyObject* prefix = PyObject_GetAttrString(sys_mod, "prefix");
        PyObject* base_prefix = PyObject_GetAttrString(sys_mod, "base_prefix");
        std::unique_ptr<PyObject, decltype(py_decref)> pref_guard(prefix, py_decref);
        std::unique_ptr<PyObject, decltype(py_decref)> base_guard(base_prefix, py_decref);

        if (prefix && base_prefix) {
            std::cout << "C++ Runtime: sys.prefix      = " << PyUnicode_AsUTF8(prefix) << "\n";
            std::cout << "C++ Runtime: sys.base_prefix = " << PyUnicode_AsUTF8(base_prefix) << "\n";
        }
    }
};

int main() {
    try {
        PythonRuntime runtime(L"/home/user/project/.venv");
        runtime.inspect_prefixes();
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
