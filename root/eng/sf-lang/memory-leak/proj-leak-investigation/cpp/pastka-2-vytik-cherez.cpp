#include <iostream>
#include <memory>
#include <vector>
#include <stdexcept>

void risky_operation(const std::vector<int> &vec) {
    if (vec.empty() || vec[0] == 0) {
        throw std::runtime_error("Критична помилка вхідного масиву");
    }
}

void safe_calculate(size_t n) {
    /* Автоматичне керування пам'яттю через std::vector (RAII) */
    std::vector<int> buffer(n, 0);
    
    /* Навіть якщо функція згенерує виняток, деструктор std::vector
       гарантовано поверне всю пам'ять купі під час розкрутки стека */
    risky_operation(buffer);
}

int main() {
    try {
        safe_calculate(1024);
    } catch (const std::exception &ex) {
        std::cout << "Перехоплено виняток: " << ex.what() 
                  << "\nПам'ять звільнено автоматично без жодного витоку!\n";
    }
    return 0;
}
