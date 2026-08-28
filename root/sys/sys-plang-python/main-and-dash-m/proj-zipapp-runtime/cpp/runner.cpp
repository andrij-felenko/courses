// runner.cpp — Сучасний C++20 завантажувач із RAII та керуванням винятками
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string_view>
#include <vector>
#include <span>

class PythonRuntime {
public:
    PythonRuntime(std::string_view pyz_path, std::span<char*> args) {
        PyConfig config;
        PyConfig_InitPythonConfig(&config);
        config.parse_argv = 1;

        PyStatus status = PyConfig_SetBytesString(&config, &config.run_filename, pyz_path.data());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося встановити шлях до zipapp архіву");
        }

        status = PyConfig_SetBytesArgv(&config, static_cast<int>(args.size()), args.data());
        if (PyStatus_Exception(status)) {
            PyConfig_Clear(&config);
            throw std::runtime_error("Не вдалося ініціалізувати аргументи argv");
        }

        status = Py_InitializeFromConfig(&config);
        PyConfig_Clear(&config);

        if (PyStatus_Exception(status)) {
            throw std::runtime_error("Фатальний збій ініціалізації ядра CPython");
        }
    }

    ~PythonRuntime() {
        if (Py_IsInitialized()) {
            Py_Finalize();
        }
    }

    PythonRuntime(const PythonRuntime&) = delete;
    PythonRuntime& operator=(const PythonRuntime&) = delete;

    [[nodiscard]] int run() noexcept {
        return Py_RunMain();
    }
};

int main(int argc, char* argv[]) {
    try {
        std::string_view pyz_file = (argc > 1) ? argv[1] : "bin/sysmon.pyz";
        std::span<char*> args(argv, static_cast<size_t>(argc));

        std::cout << "[C++ Host] Ініціалізація CPython для: " << pyz_file << std::endl;
        PythonRuntime runtime(pyz_file, args);
        int exit_code = runtime.run();
        std::cout << "[C++ Host] Код завершення: " << exit_code << std::endl;
        return exit_code;
    } catch (const std::exception& ex) {
        std::cerr << "[C++ Error] " << ex.what() << std::endl;
        return 1;
    }
}
