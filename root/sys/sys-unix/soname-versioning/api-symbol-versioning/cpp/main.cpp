// main.cpp — Ідіоматична обгортка RAII для dlvsym у C++
#define _GNU_SOURCE
#include <iostream>
#include <memory>
#include <string_view>
#include <stdexcept>
#include <dlfcn.h>

// RAII обгортка для безпечного керування ресурсами dlopen/dlclose
class SharedLibrary {
    void* handle_{nullptr};
public:
    explicit SharedLibrary(std::string_view filepath) {
        handle_ = dlopen(filepath.data(), RTLD_LAZY);
        if (!handle_) {
            throw std::runtime_error(std::string("Не вдалося відкрити бібліотеку: ") + dlerror());
        }
    }

    ~SharedLibrary() {
        if (handle_) {
            dlclose(handle_);
        }
    }

    // Забороняємо копіювання для запобігання подвійному закриттю дескриптора
    SharedLibrary(const SharedLibrary&) = delete;
    SharedLibrary& operator=(const SharedLibrary&) = delete;

    // Шаблонний метод для безпечного отримання версіонованого покажчика
    template<typename FuncSignature>
    FuncSignature get_versioned_symbol(std::string_view symbol, std::string_view version) const {
        dlerror(); // Скидаємо попередній стан помилки
        void* ptr = dlvsym(handle_, symbol.data(), version.data());
        const char* err = dlerror();
        if (err) {
            throw std::runtime_error(std::string("Символ ") + symbol.data() + 
                                     "@" + version.data() + " не знайдено: " + err);
        }
        return reinterpret_cast<FuncSignature>(ptr);
    }
};

void run_dynamic_test() {
    try {
        SharedLibrary lib("libfoo.so.1");

        using func_v1_t = int(*)(int);
        using func_v2_t = int(*)(int, int);

        auto func_v1 = lib.get_versioned_symbol<func_v1_t>("foo_process", "LIBFOO_1.0");
        std::cout << "[C++ Client] Виклик foo_process@LIBFOO_1.0(42) повернув: " 
                  << func_v1(42) << "\n";

        auto func_v2 = lib.get_versioned_symbol<func_v2_t>("foo_process", "LIBFOO_2.0");
        std::cout << "[C++ Client] Виклик foo_process@@LIBFOO_2.0(42, 100) повернув: " 
                  << func_v2(42, 100) << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "[C++ Error] " << ex.what() << "\n";
    }
}
