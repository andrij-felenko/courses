// calc.cpp
#include "calc.hpp"
#include <iostream>

namespace calc {
    int calculate_checksum(std::string_view data) noexcept {
        int sum = 0;
        for (unsigned char ch : data) {
            sum = (sum * 31) + ch;
        }
        return sum;
    }

    void print_build_banner() noexcept {
        // Пастка 1: використання часу компіляції
        std::cout << "Calc Engine Build Date: " << __DATE__ << " " << __TIME__ << "\n";
        // Пастка 2: використання абсолютного шляху до файлу
        std::cout << "Compiled from source: " << __FILE__ << "\n";
    }
}
