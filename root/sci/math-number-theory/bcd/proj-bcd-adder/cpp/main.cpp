#include <iostream>
#include <cstdint>
#include <iomanip>

// 1. Структура для зберігання результату та прапорців
struct BcdResult {
    uint8_t value;     // 8-бітний результат
    bool carry;        // Прапорець перенесення за межі байта (CF)
    bool half_carry;   // Прапорець перенесення між тетрадами (AF)
};

// 2. Допоміжна функція для друку двійкового значення байта
void print_bin(uint8_t val) {
    for (int i = 7; i >= 0; --i) {
        std::cout << ((val >> i) & 1);
        if (i == 4) std::cout << " "; // пробіл між тетрадами
    }
}

// 3. Функція звичайного двійкового додавання з генерацією прапорців
BcdResult binary_add(uint8_t a, uint8_t b) {
    BcdResult res;
    
    // Додаємо нижні тетради для визначення AF (Half-Carry)
    uint8_t low_sum = (a & 0x0F) + (b & 0x0F);
    res.half_carry = (low_sum > 0x0F);
    
    // Повне додавання (з використанням 16 біт для виловлення CF)
    uint16_t full_sum = static_cast<uint16_t>(a) + b;
    res.value = static_cast<uint8_t>(full_sum & 0xFF);
    res.carry = (full_sum > 0xFF);
    
    return res;
}

// 4. Головна функція BCD корекції (аналог інструкції DAA)
BcdResult bcd_adjust(BcdResult bin_res) {
    BcdResult adjusted = bin_res;
    uint8_t correction = 0;

    // Крок A: Корекція нижньої тетради
    uint8_t low_nibble = adjusted.value & 0x0F;
    if (low_nibble > 9 || adjusted.half_carry) {
        correction += 0x06;
    }

    // Крок B: Корекція верхньої тетради
    uint8_t high_nibble = (adjusted.value >> 4) & 0x0F;
    if (high_nibble > 9 || adjusted.carry || ((high_nibble == 9) && (low_nibble > 9))) {
        correction += 0x60;
        adjusted.carry = true; // Корекція верхньої тетради генерує остаточний перенос
    }

    // Додаємо корекцію
    adjusted.value += correction;
    return adjusted;
}

// 5. Тестування роботи суматора
int main() {
    // Тестовий випадок: 28 + 49 = 77
    uint8_t num1 = 0x28; // BCD формат для 28
    uint8_t num2 = 0x49; // BCD формат для 49
    
    std::cout << "Додаємо BCD числа: 28 та 49\n\n";

    // Двійкове додавання
    BcdResult step1 = binary_add(num1, num2);
    
    std::cout << "Крок 1: Двійкове додавання\n";
    std::cout << "  "; print_bin(num1); std::cout << " (28)\n";
    std::cout << "+ "; print_bin(num2); std::cout << " (49)\n";
    std::cout << "  ---------\n";
    std::cout << "  "; print_bin(step1.value); 
    std::cout << " (Прапорці: AF=" << step1.half_carry << ", CF=" << step1.carry << ")\n\n";

    // BCD корекція
    BcdResult final_res = bcd_adjust(step1);
    
    std::cout << "Крок 2: Корекція +6 (DAA)\n";
    std::cout << "  "; print_bin(final_res.value); 
    std::cout << " (Результат в BCD: " << std::hex << (int)final_res.value << ")\n";
    std::cout << "Остаточний CF (сотні): " << final_res.carry << "\n";

    return 0;
}
