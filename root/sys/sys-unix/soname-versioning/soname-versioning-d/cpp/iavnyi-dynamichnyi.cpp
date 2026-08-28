#define _GNU_SOURCE
#include <iostream>
#include <string_view>
#include <dlfcn.h>

class PluginLoader {
    void* handle_{nullptr};
public:
    explicit PluginLoader(std::string_view path) 
        : handle_(dlopen(path.data(), RTLD_LAZY)) {}

    ~PluginLoader() {
        if (handle_) dlclose(handle_);
    }

    template<typename FuncPtr>
    FuncPtr get_symbol(std::string_view name, std::string_view version) const {
        return reinterpret_cast<FuncPtr>(dlvsym(handle_, name.data(), version.data()));
    }
};

void execute_plugin() {
    PluginLoader plugin("libfoo.so.1");
    using func_v1_t = int(*)(int);
    
    if (auto func = plugin.get_symbol<func_v1_t>("foo_process", "LIBFOO_1.0")) {
        std::cout << "Результат виклику v1: " << func(42) << "\n";
    }
}
