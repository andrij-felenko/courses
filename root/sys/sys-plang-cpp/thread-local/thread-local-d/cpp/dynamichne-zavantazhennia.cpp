// Ідіоматичне C++ RAII-завантаження динамічного модуля
#include <dlfcn.h>
#include <iostream>
#include <memory>
#include <stdexcept>

class DynamicModule {
    void* handle_{nullptr};
public:
    explicit DynamicModule(const char* path) {
        handle_ = dlopen(path, RTLD_NOW);
        if (!handle_) {
            throw std::runtime_error(dlerror());
        }
    }
    ~DynamicModule() {
        if (handle_) dlclose(handle_);
    }
    template<typename T>
    T get_symbol(const char* name) const {
        return reinterpret_cast<T>(dlsym(handle_, name));
    }
};
