#include <iostream>
#include <cmath>
#include <iomanip>
#include <vector>
#include <string>

// Структура для зберігання результатів для однієї основи
struct RadixResult {
    int base;
    int digits_needed;
    int total_hardware_cost;
    double efficiency_ratio;
};

// Головна обчислювальна функція для оцінки економічності
RadixResult calculate_economy(int base, double target_number, int reference_cost) {
    RadixResult res;
    res.base = base;
    
    // Кількість розрядів: обчислюємо логарифм за основою b і беремо стелю
    // std::log() обчислює натуральний логарифм. Використовуємо властивість log_b(x) = ln(x) / ln(b)
    res.digits_needed = static_cast<int>(std::ceil(std::log(target_number) / std::log(base)));
    
    // Загальні апаратні витрати: кількість розрядів помножена на кількість станів
    res.total_hardware_cost = base * res.digits_needed;
    
    // Ефективність відносно двійкової системи (якщо reference_cost задано)
    if (reference_cost > 0) {
        res.efficiency_ratio = static_cast<double>(reference_cost) / res.total_hardware_cost;
    } else {
        res.efficiency_ratio = 1.0;
    }
    return res;
}

int main() {
    // Цільове число для зберігання: 1 мільярд (10^9)
    double target_N = 1e9;
    
    std::cout << "Аналіз апаратних витрат для збереження числа N = 1,000,000,000\n";
    std::cout << std::string(65, '-') << "\n";
    std::cout << std::setw(10) << "Основа" 
              << std::setw(15) << "Розрядів" 
              << std::setw(20) << "Загальні витрати" 
              << std::setw(20) << "Ефективність (до b=2)" << "\n";
    std::cout << std::string(65, '-') << "\n";

    // Спочатку розраховуємо метрики для двійкової системи, щоб мати еталон для порівняння
    RadixResult ref_result = calculate_economy(2, target_N, 0);
    int ref_cost = ref_result.total_hardware_cost;

    // Масив основ для аналізу
    std::vector<int> bases_to_test = {2, 3, 4, 8, 10, 16};

    // Проходимо по всіх основах та обчислюємо їхню економічність
    for (int b : bases_to_test) {
        RadixResult r = calculate_economy(b, target_N, ref_cost);
        std::cout << std::setw(10) << r.base 
                  << std::setw(15) << r.digits_needed 
                  << std::setw(20) << r.total_hardware_cost 
                  << std::fixed << std::setprecision(3) << std::setw(18) << r.efficiency_ratio << "x\n";
    }

    return 0;
}
