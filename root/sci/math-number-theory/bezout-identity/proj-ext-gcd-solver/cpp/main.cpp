#include <iostream>
#include <tuple>
#include <stdexcept>

// Структура для зберігання результату розширеного алгоритму Евкліда
struct ExtGcdResult {
    long long gcd; // Найбільший спільний дільник
    long long x;   // Коефіцієнт Безу для a
    long long y;   // Коефіцієнт Безу для b
};

// Функція розширеного алгоритму Евкліда
// Повертає структуру ExtGcdResult, де a*x + b*y = gcd(a, b)
ExtGcdResult extended_gcd(long long a, long long b) {
    // Початкові значення для алгоритму
    long long old_r = a, r = b;
    long long old_x = 1, x = 0;
    long long old_y = 0, y = 1;
    
    // Цикл працює, поки остача не стане рівною нулю
    while (r != 0) {
        long long quotient = old_r / r;
        
        // Оновлюємо остачі
        long long temp_r = r;
        r = old_r - quotient * r;
        old_r = temp_r;
        
        // Оновлюємо коефіцієнти x
        long long temp_x = x;
        x = old_x - quotient * x;
        old_x = temp_x;
        
        // Оновлюємо коефіцієнти y
        long long temp_y = y;
        y = old_y - quotient * y;
        old_y = temp_y;
    }
    
    // old_r містить НСД, old_x та old_y містять коефіцієнти Безу
    return {old_r, old_x, old_y};
}

// Приклад використання для пошуку оберненого елемента за модулем
long long mod_inverse(long long a, long long m) {
    if (m <= 0) {
        throw std::invalid_argument("Модуль має бути додатним числом");
    }
    
    ExtGcdResult result = extended_gcd(a, m);
    
    // Якщо НСД(a, m) != 1, оберненого елемента не існує
    if (result.gcd != 1 && result.gcd != -1) {
        throw std::runtime_error("Оберненого елемента не існує (числа не взаємно прості)");
    }
    
    // Коефіцієнт x може бути від'ємним, тому приводимо його до діапазону [0, m-1]
    long long res = (result.x % m + m) % m;
    return res;
}

int main() {
    long long a = 73;
    long long b = 22;
    
    ExtGcdResult res = extended_gcd(a, b);
    
    std::cout << "GCD(" << a << ", " << b << ") = " << res.gcd << std::endl;
    std::cout << "Коефіцієнти Безу: x = " << res.x << ", y = " << res.y << std::endl;
    std::cout << "Перевірка: " << a << " * (" << res.x << ") + " << b << " * (" << res.y << ") = " 
              << (a * res.x + b * res.y) << std::endl;
              
    // Тестуємо обернений елемент
    try {
        long long inv = mod_inverse(a, b);
        std::cout << "Обернений елемент " << a << " mod " << b << " = " << inv << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Помилка: " << e.what() << std::endl;
    }
    
    return 0;
}
