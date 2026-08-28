#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <memory>
#include <span>
#include <string_view>
#include <vector>
#include <expected>

namespace cpython_diag {

class ConfigInspector {
public:
    static std::expected<std::vector<std::wstring>, std::string_view> get_resolved_search_paths() {
        PyConfig config;
        PyConfig_InitPythonConfig(&config);

        // Автоматичне очищення пам'яті конфігурації при виході з області видимості (RAII)
        struct ConfigCleaner {
            PyConfig& cfg;
            ~ConfigCleaner() { PyConfig_Clear(&cfg); }
        } cleaner{config};

        PyStatus status = PyConfig_Read(&config);
        if (PyStatus_Exception(status)) {
            return std::unexpected("Не вдалося прочитати системну конфігурацію CPython");
        }

        std::vector<std::wstring> paths;
        paths.reserve(config.module_search_paths.length);

        std::span<wchar_t*> items_span(
            config.module_search_paths.items, 
            config.module_search_paths.length
        );

        for (const wchar_t* path_str : items_span) {
            if (path_str != nullptr) {
                paths.emplace_back(path_str);
            }
        }

        return paths;
    }
};

} // namespace cpython_diag
