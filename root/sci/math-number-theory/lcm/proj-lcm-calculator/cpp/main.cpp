#include <iostream>
#include <vector>
#include <numeric>
#include <cmath>

// 1. Компонент безпечного НСК для пари
long long safe_lcm(long long a, long long b) {
    // Крайовий випадок 1: захист від ділення на нуль
    if (a == 0 || b == 0) {
        return 0;
    }
    
    // Крайовий випадок 2: нормалізація від'ємних чисел
    // НСК за визначенням є додатним числом
    a = std::abs(a);
    b = std::abs(b);
    
    // Ядро алгоритму: ділення передує множенню
    return (a / std::gcd(a, b)) * b;
}

// 2. Компонент згортки для масиву
long long array_lcm(const std::vector<long long>& numbers) {
    // Захист від порожнього вводу
    if (numbers.empty()) {
        return 0;
    }
    
    long long result = numbers[0];
    
    for (size_t i = 1; i < numbers.size(); ++i) {
        // Оптимізація раннього виходу (Early Exit)
        if (result == 0) {
            break;
        }
        result = safe_lcm(result, numbers[i]);
    }
    
    return result;
}
