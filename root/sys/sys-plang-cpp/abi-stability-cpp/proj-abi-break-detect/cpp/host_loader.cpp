// host_loader.cpp — безпечне динамічне завантаження плагіна
#include "plugin_abi.hpp"
#include <iostream>
#include <vector>

#if defined(_WIN32)
  #include <windows.h>
  using ModuleHandle = HMODULE;
  #define LOAD_LIB(path) LoadLibraryA(path)
  #define GET_SYM(mod, name) GetProcAddress(mod, name)
  #define CLOSE_LIB(mod) FreeLibrary(mod)
#else
  #include <dlfcn.h>
  using ModuleHandle = void*;
  #define LOAD_LIB(path) dlopen(path, RTLD_NOW | RTLD_LOCAL)
  #define GET_SYM(mod, name) dlsym(mod, name)
  #define CLOSE_LIB(mod) dlclose(mod)
#endif

class DynamicPluginHost {
public:
    explicit DynamicPluginHost(const char* library_path) {
        module_ = LOAD_LIB(library_path);
        if (!module_) {
            throw std::runtime_error("Помилка завантаження бібліотеки плагіна");
        }

        // Перевірка наявності точки отримання метаданих
        auto get_meta = reinterpret_cast<decltype(&plugin_get_metadata)>(GET_SYM(module_, "plugin_get_metadata"));
        if (!get_meta) {
            CLOSE_LIB(module_);
            throw std::runtime_error("Бібліотека не містить точки входу plugin_get_metadata");
        }

        plugin_metadata_t meta{};
        if (get_meta(&meta) == PLUGIN_SUCCESS) {
            std::cout << "Завантажено плагін: " << meta.plugin_name 
                      << " версія ABI: " << meta.abi_version_major << "." << meta.abi_version_minor << "\n";
            if (meta.abi_version_major != 1) {
                CLOSE_LIB(module_);
                throw std::runtime_error("Несумісна major-версія ABI плагіна!");
            }
        }
    }

    ~DynamicPluginHost() {
        if (module_) {
            CLOSE_LIB(module_);
        }
    }

private:
    ModuleHandle module_ = nullptr;
};
