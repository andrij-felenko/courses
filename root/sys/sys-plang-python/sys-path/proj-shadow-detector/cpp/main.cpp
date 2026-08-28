#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <filesystem>
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <vector>
#include <expected>

namespace py_embed {

namespace fs = std::filesystem;

class ScopedPyConfig {
public:
    ScopedPyConfig() {
        PyConfig_InitPythonConfig(&config_);
    }

    ~ScopedPyConfig() {
        PyConfig_Clear(&config_);
    }

    ScopedPyConfig(const ScopedPyConfig&) = delete;
    ScopedPyConfig& operator=(const ScopedPyConfig&) = delete;

    PyConfig& get() noexcept { return config_; }
    const PyConfig& get() const noexcept { return config_; }

private:
    PyConfig config_;
};

enum class InitError {
    ConfigError,
    InsecureRelativePath,
    BootstrapFailed
};

class SafePythonRuntime {
public:
    static std::expected<SafePythonRuntime, InitError> create(
        std::wstring_view program_name,
        std::span<const fs::path> allowed_library_paths) 
    {
        ScopedPyConfig scoped_cfg;
        PyConfig& cfg = scoped_cfg.get();

        cfg.isolated = 1;
        cfg.safe_path = 1;
        cfg.use_environment = 0;

        PyStatus status = PyConfig_SetString(&cfg, &cfg.program_name, program_name.data());
        if (PyStatus_Exception(status)) {
            return std::unexpected(InitError::ConfigError);
        }

        cfg.module_search_paths_set = 1;
        for (const auto& dir_path : allowed_library_paths) {
            // Сувора C++ перевірка: шлях повинен бути абсолютним
            if (!dir_path.is_absolute()) {
                std::cerr << "Безпековий дефект: заборонено неабсолютний шлях: " 
                          << dir_path << '\n';
                return std::unexpected(InitError::InsecureRelativePath);
            }

            status = PyWideStringList_Append(&cfg.module_search_paths, dir_path.c_str());
            if (PyStatus_Exception(status)) {
                return std::unexpected(InitError::ConfigError);
            }
        }

        status = Py_InitializeFromConfig(&cfg);
        if (PyStatus_Exception(status)) {
            return std::unexpected(InitError::BootstrapFailed);
        }

        return SafePythonRuntime{};
    }

    ~SafePythonRuntime() {
        if (Py_IsInitialized()) {
            Py_FinalizeEx();
        }
    }

    SafePythonRuntime(SafePythonRuntime&&) noexcept = default;
    SafePythonRuntime& operator=(SafePythonRuntime&&) noexcept = default;

private:
    SafePythonRuntime() = default;
};

} // namespace py_embed
