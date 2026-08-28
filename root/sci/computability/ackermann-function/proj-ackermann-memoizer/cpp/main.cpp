#include <iostream>
#include <map>
#include <utility>

// Використовуємо 64-бітні беззнакові цілі числа для уникнення швидкого переповнення
using uint64 = unsigned long long;

// Тип для ключа кешу (пара m та n)
using CacheKey = std::pair<uint64, uint64>;

// Глобальний кеш для зберігання вже обчислених значень A(m, n)
std::map<CacheKey, uint64> memo_cache;

uint64 ackermann(uint64 m, uint64 n) {
    // Базовий випадок: m = 0
    if (m == 0) {
        return n + 1;
    }

    // Створюємо ключ для поточних аргументів
    CacheKey key = {m, n};

    // Перевіряємо, чи результат вже є в кеші
    if (memo_cache.find(key) != memo_cache.end()) {
        return memo_cache[key];
    }

    uint64 result;
    
    // Рекурсивні випадки
    if (n == 0) {
        result = ackermann(m - 1, 1);
    } else {
        result = ackermann(m - 1, ackermann(m, n - 1));
    }

    // Зберігаємо результат у кеші перед поверненням
    memo_cache[key] = result;
    
    return result;
}

int main() {
    std::cout << "Обчислення функції Аккермана з мемоїзацією\n";
    std::cout << "-------------------------------------------\n";

    // Обчислимо кілька значень
    for (uint64 m = 0; m <= 3; ++m) {
        for (uint64 n = 0; n <= 4; ++n) {
            std::cout << "A(" << m << ", " << n << ") = " << ackermann(m, n) << "\n";
        }
    }

    // Спробуємо обчислити більше значення (A(4, 0))
    // Увага: A(4, 1) = 65533 вже потребує глибокої рекурсії, 
    // але завдяки мемоїзації та збільшенню розміру стека ОС це можливо обчислити.
    // A(4, 2) має 19729 десяткових цифр і не поміститься у uint64.
    
    std::cout << "\nРозширене обчислення:\n";
    std::cout << "A(4, 0) = " << ackermann(4, 0) << "\n";
    
    // Статистика кешу
    std::cout << "\nКількість елементів у кеші: " << memo_cache.size() << "\n";

    return 0;
}
