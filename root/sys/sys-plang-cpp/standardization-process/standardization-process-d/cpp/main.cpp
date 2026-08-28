// Перевірка підтримки окремих мовних та бібліотечних можливостей
#include <version>

#if defined(__cpp_lib_print) && __cpp_lib_print >= 202207L
    #include <print>
    void output_message(const char* name, int score) {
        std::println("Користувач: {}, Бали: {}", name, score);
    }
#else
    #include <iostream>
    void output_message(const char* name, int score) {
        std::cout << "Користувач: " << name << ", Бали: " << score << "\n";
    }
#endif
