#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string_view>
#include <memory>
#include <stdexcept>

// RAII-обгортка для автоматичного керування часом життя об'єктів PyObject*
struct PyObjectDeleter {
    void operator()(PyObject* obj) const noexcept {
        if (obj) {
            Py_DECREF(obj);
        }
    }
};

using UniquePyObject = std::unique_ptr<PyObject, PyObjectDeleter>;

/**
 * Ідіоматичний C++20 клас для імпорту модулів із пам'яті через C-API.
 */
class MemoryModuleImporter {
public:
    /**
     * Створює та завантажує модуль у середовище виконання CPython.
     */
    static void import_from_memory(std::string_view module_name, std::string_view source_code) {
        // 1. Компіляція вихідного тексту в об'єкт коду
        UniquePyObject code_obj(Py_CompileString(
            source_code.data(),
            "<in-memory-cpp>",
            Py_file_input
        ));

        if (!code_obj) {
            throw std::runtime_error("Помилка компіляції коду в PyCodeObject");
        }

        // 2. Створення та виконання модуля в пам'яті
        UniquePyObject module(PyImport_ExecCodeModule(
            module_name.data(),
            code_obj.get()
        ));

        if (!module) {
            throw std::runtime_error("Помилка виконання модуля в PyImport_ExecCodeModule");
        }

        std::cout << "Модуль '" << module_name << "' успішно ініціалізовано в C++ оточенні\n";
    }
};
