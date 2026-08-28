#include <iostream>
#include <memory>

// У C++ подібні макроси замінюють на RAII-обгортки або звичайні лямбда-виклики
inline void safe_cleanup(std::unique_ptr<int>& ptr) noexcept {
    ptr.reset();
    std::cout << "Ресурс звільнено через RAII\n";
}

int main() {
    auto data = std::make_unique<int>(42);
    bool ok = true;

    if (ok)
        safe_cleanup(data);
    else
        std::cout << "Помилка\n";

    return 0;
}
