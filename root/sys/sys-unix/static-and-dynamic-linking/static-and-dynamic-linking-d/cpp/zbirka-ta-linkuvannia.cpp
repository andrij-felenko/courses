// Збірка та робота з динамічним завантаженням через C++ RAII
#include <iostream>
#include <memory>
#include <dlfcn.h>

// Оголошення сигнатури функції
using SquareFn = int(*)(int);

struct DlCloser {
    void operator()(void* h) const { if (h) dlclose(h); }
};

int main() {
    // Явне динамічне завантаження бібліотеки під час виконання
    std::unique_ptr<void, DlCloser> handle(dlopen("./libmy_math.so", RTLD_LAZY));
    if (!handle) {
        std::cerr << "Помилка відкриття .so: " << dlerror() << '\n';
        return 1;
    }

    // Отримання вказівника на функцію
    auto square_func = reinterpret_cast<SquareFn>(dlsym(handle.get(), "square"));
    if (!square_func) {
        std::cerr << "Помилка dlsym: " << dlerror() << '\n';
        return 1;
    }

    std::cout << "Динамічний виклик square(5): " << square_func(5) << '\n';
    return 0;
}
