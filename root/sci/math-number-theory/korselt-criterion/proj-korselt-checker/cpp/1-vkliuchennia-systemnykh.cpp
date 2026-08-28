#include <iostream>
#include <vector>
#include <string>
#include <cstdint>

// Базова функція для безпечного отримання вхідного цілого числа від користувача
uint64_t getInput(int argc, char* argv[]) {
    if (argc > 1) {
        return std::stoull(argv[1]);
    }
    uint64_t n;
    std::cout << "Введіть ціле додатне число для перевірки: ";
    std::cin >> n;
    return n;
}
