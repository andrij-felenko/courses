// console_utf8.cpp — RAII-обгортка ініціалізації консолі в C++
#include <windows.h>
#include <iostream>

class ConsoleUtf8Guard {
public:
    ConsoleUtf8Guard() 
        : old_out_cp_(GetConsoleOutputCP()), 
          old_in_cp_(GetConsoleCP()) 
    {
        SetConsoleOutputCP(CP_UTF8);
        SetConsoleCP(CP_UTF8);
    }

    ~ConsoleUtf8Guard() noexcept {
        // Відновлюємо попередні кодові сторінки термінала
        SetConsoleOutputCP(old_out_cp_);
        SetConsoleCP(old_in_cp_);
    }

    ConsoleUtf8Guard(const ConsoleUtf8Guard&) = delete;
    ConsoleUtf8Guard& operator=(const ConsoleUtf8Guard&) = delete;

private:
    UINT old_out_cp_;
    UINT old_in_cp_;
};

int main() {
    const ConsoleUtf8Guard console_guard;
    std::cout << "Тестовий вивід Unicode: Привіт, світе! 🚀\n";
    return 0;
}
