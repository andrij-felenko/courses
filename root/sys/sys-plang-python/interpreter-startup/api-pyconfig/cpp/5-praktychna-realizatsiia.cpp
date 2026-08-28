#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

namespace py {

/* RAII-обгортка над ресурсами структури PyConfig */
class ScopedConfig {
public:
    explicit ScopedConfig(bool isolated = true) {
        if (isolated) {
            PyConfig_InitIsolatedConfig(&config_);
        } else {
            PyConfig_InitPythonConfig(&config_);
        }
    }

    ~ScopedConfig() noexcept {
        PyConfig_Clear(&config_);
    }

    ScopedConfig(const ScopedConfig&) = delete;
    ScopedConfig& operator=(const ScopedConfig&) = delete;
    ScopedConfig(ScopedConfig&&) noexcept = delete;
    ScopedConfig& operator=(ScopedConfig&&) noexcept = delete;

    PyConfig& get() noexcept { return config_; }

    void set_program_name(const std::wstring& name) {
        check_status(PyConfig_SetString(&config_, &config_.program_name, name.c_str()));
    }

    void set_search_paths(const std::vector<std::wstring>& paths) {
        config_.module_search_paths_set = 1;
        for (const auto& path : paths) {
            check_status(PyWideStringList_Append(&config_.module_search_paths, path.c_str()));
        }
    }

    void initialize_runtime() {
        check_status(Py_InitializeFromConfig(&config_));
    }

private:
    PyConfig config_;

    static void check_status(const PyStatus& status) {
        if (PyStatus_Exception(status)) {
            if (status.err_msg) {
                throw std::runtime_error(std::string("CPython Init Error: ") + status.err_msg);
            }
            throw std::runtime_error("CPython Init Error (exit code " + std::to_string(status.exitcode) + ")");
        }
    }
};

/* RAII-обгортка над середовищем виконання CPython */
class ScopedRuntime {
public:
    explicit ScopedRuntime(ScopedConfig& config) {
        config.initialize_runtime();
    }

    ~ScopedRuntime() noexcept {
        if (Py_IsInitialized()) {
            Py_Finalize();
        }
    }

    ScopedRuntime(const ScopedRuntime&) = delete;
    ScopedRuntime& operator=(const ScopedRuntime&) = delete;
    ScopedRuntime(ScopedRuntime&&) noexcept = delete;
    ScopedRuntime& operator=(ScopedRuntime&&) noexcept = delete;

    void execute(const std::string& script) const {
        if (PyRun_SimpleString(script.c_str()) != 0) {
            throw std::runtime_error("Python execution failed");
        }
    }
};

} // namespace py

int main() {
    try {
        py::ScopedConfig config(true);
        config.get().site_import = 0;
        config.get().write_bytecode = 0;
        config.get().safe_path = 1;

        config.set_program_name(L"embedded_cpp_runtime_host");
        config.set_search_paths({L"/usr/lib/python3.12"});

        py::ScopedRuntime runtime(config);
        runtime.execute("import sys\n"
                        "print(f'[C++ Host] Runtime online. sys.path: {sys.path}')\n"
                        "print(f'[C++ Host] no_site flag: {sys.flags.no_site}')\n");
    } catch (const std::exception& ex) {
        std::cerr << "CPython initialization error: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
