#include <dlfcn.h>
#include <stdexcept>
#include <string>

// Сигнатури чистих C-функцій без витоку STL-типів
using InitFunc = int (*)(const char*);
using ProcessFunc = int (*)(const char*, char*, int);

class DynamicPluginLoader {
    void* handle_{nullptr};
    InitFunc init_fn_{nullptr};
    ProcessFunc process_fn_{nullptr};

public:
    explicit DynamicPluginLoader(const char* lib_path) {
        // Завантаження бібліотеки в ізольованому просторі імен
        handle_ = dlopen(lib_path, RTLD_NOW | RTLD_LOCAL);
        if (!handle_) {
            throw std::runtime_error(std::string("Не вдалося завантажити бібліотеку: ") + dlerror());
        }

        // Отримання адрес чистих C-функцій
        init_fn_ = reinterpret_cast<InitFunc>(dlsym(handle_, "plugin_init"));
        process_fn_ = reinterpret_cast<ProcessFunc>(dlsym(handle_, "plugin_process"));

        if (!init_fn_ || !process_fn_) {
            dlclose(handle_);
            throw std::runtime_error("Символи інтерфейсу не знайдено в завантаженій бібліотеці");
        }
    }

    ~DynamicPluginLoader() {
        if (handle_) {
            dlclose(handle_);
        }
    }
};
