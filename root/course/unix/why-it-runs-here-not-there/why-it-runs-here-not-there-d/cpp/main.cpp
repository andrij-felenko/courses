#include <iostream>
#include <locale>
#include <clocale>

void init_runtime_locale() {
    // Спроба встановити глобальну локаль C++ з оточення
    try {
        std::locale::global(std::locale(""));
        std::cin.imbue(std::locale());
        std::cout.imbue(std::locale());
    } catch (const std::runtime_error &) {
        // Fallback на безпечну локаль C.UTF-8 або класичну C
        try {
            std::locale::global(std::locale("C.UTF-8"));
        } catch (...) {
            std::locale::global(std::locale::classic());
        }
    }
    // Фіксація числового форматування C для надійного парсингу float/double
    std::setlocale(LC_NUMERIC, "C");
}
