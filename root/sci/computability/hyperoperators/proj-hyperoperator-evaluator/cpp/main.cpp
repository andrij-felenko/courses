#include <iostream>
#include <string>
#include <stdexcept>
#include <cmath>

// Компонент 1: Обробка помилок
class OverflowException : public std::runtime_error {
public:
    OverflowException() : std::runtime_error("Переповнення типу під час обчислення.") {}
};

// Компонент 2: Базові гіпероператори (оптимізація базису)
uint64_t successor(uint64_t b) {
    if (b == UINT64_MAX) throw OverflowException();
    return b + 1;
}

uint64_t addition(uint64_t a, uint64_t b) {
    if (UINT64_MAX - a < b) throw OverflowException();
    return a + b;
}

uint64_t multiplication(uint64_t a, uint64_t b) {
    if (a == 0 || b == 0) return 0;
    if (UINT64_MAX / a < b) throw OverflowException();
    return a * b;
}

uint64_t exponentiation(uint64_t a, uint64_t b) {
    if (b == 0) return 1;
    if (a == 0) return 0;
    uint64_t result = 1;
    for (uint64_t i = 0; i < b; ++i) {
        if (UINT64_MAX / result < a) throw OverflowException();
        result *= a;
    }
    return result;
}

// Компонент 3: Універсальне рекурсивне ядро
uint64_t hyperoperate(unsigned int n, uint64_t a, uint64_t b) {
    if (n == 0) return successor(b);
    if (n == 1) return addition(a, b);
    if (n == 2) return multiplication(a, b);
    if (n == 3) return exponentiation(a, b);

    if (b == 0) return 1; 

    uint64_t inner_result = hyperoperate(n, a, b - 1);
    return hyperoperate(n - 1, a, inner_result);
}

// Компонент 4: Форматувальник виводу (Нотація Кнута)
std::string format_knuth(unsigned int n, uint64_t a, uint64_t b) {
    if (n <= 2) {
        if (n == 1) return std::to_string(a) + " + " + std::to_string(b);
        if (n == 2) return std::to_string(a) + " * " + std::to_string(b);
    }
    std::string arrows = "";
    for (unsigned int i = 0; i < n - 2; ++i) {
        arrows += "↑";
    }
    return std::to_string(a) + " " + arrows + " " + std::to_string(b);
}

// Компонент 5: Головний цикл симуляції
int main() {
    std::cout << "--- Симулятор гіпероператорів ---" << std::endl;
    
    struct Scenario { unsigned int n; uint64_t a; uint64_t b; };
    Scenario tests[] = {
        {1, 5, 3},       
        {2, 4, 5},       
        {3, 2, 8},       
        {4, 2, 4},       
        {4, 3, 2},       
        {5, 2, 3}        
    };

    for (const auto& test : tests) {
        std::cout << "Запит: " << format_knuth(test.n, test.a, test.b) << std::endl;
        try {
            uint64_t result = hyperoperate(test.n, test.a, test.b);
            std::cout << "Результат: " << result << std::endl << std::endl;
        } catch (const OverflowException& e) {
            std::cout << "Помилка: " << e.what() << std::endl << std::endl;
        }
    }

    return 0;
}
