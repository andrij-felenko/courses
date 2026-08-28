// main_host.cpp — Ідіоматичний C++20 завантажувач модуля з RAII
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string_view>
#include <span>

class EmbeddedPythonHost {
public:
    explicit EmbeddedPythonHost(std::string_view module_name, std::span<char*> args) {
        PyConfig config;
        PyConfig_InitPythonConfig(&config);
        config.parse_argv = 1;

        PyStatus status = PyConfig_SetBytesString(&config, &config.run_module, module_name.data());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося сконфігурувати цільовий модуль run_module");
        }

        status = PyConfig_SetBytesArgv(&config, static_cast<int>(args.size()), args.data());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося ініціалізувати масив аргументів CLI");
        }

        status = Py_InitializeFromConfig(&config);
        PyConfig_Clear(&config);

        if (PyStatus_Exception(status)) {
            throw std::runtime_error("Помилка розгортання структур середовища CPython");
        }
    }

    ~EmbeddedPythonHost() {
        if (Py_IsInitialized()) {
            Py_Finalize();
        }
    }

    EmbeddedPythonHost(const EmbeddedPythonHost&) = delete;
    EmbeddedPythonHost& operator=(const EmbeddedPythonHost&) = delete;

    [[nodiscard]] int execute() noexcept {
        return Py_RunMain();
    }
};

int main(int argc, char* argv[]) {
    try {
        std::string_view target_module = (argc > 1) ? argv[1] : "http.server";
        std::span<char*> args(argv, static_cast<size_t>(argc));

        std::cout << "[Host C++] Ініціалізація CPython для модуля: " << target_module << std::endl;
        EmbeddedPythonHost host(target_module, args);
        int exit_code = host.execute();
        std::cout << "[Host C++] Виконання модуля завершено з кодом: " << exit_code << std::endl;
        return exit_code;
    } catch (const std::exception& err) {
        std::cerr << "[Host C++ Error] " << err.what() << std::endl;
        return 1;
    }
}
