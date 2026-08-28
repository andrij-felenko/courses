#include <iostream>
#include <cstring>
#include <cstdint>
#include <iomanip>

// Маска для знакового біта (31-й біт)
constexpr uint32_t SIGN_BIT_MASK = 0x80000000;

// Функція для перевірки знакового біта
bool is_negative(float value) {
    uint32_t bits;
    // Безпечне копіювання бітів з float у uint32_t
    std::memcpy(&bits, &value, sizeof(bits));
    
    // Побітове І з маскою залишає тільки знаковий біт
    return (bits & SIGN_BIT_MASK) != 0;
}

// Функція для швидкої зміни знаку (заміна value = -value)
float flip_sign(float value) {
    uint32_t bits;
    std::memcpy(&bits, &value, sizeof(bits));
    
    // Побітове АБО-НЕ (XOR) інвертує лише знаковий біт
    bits ^= SIGN_BIT_MASK;
    
    float result;
    std::memcpy(&result, &bits, sizeof(result));
    return result;
}

// Функція для знаходження модуля (абсолютної величини)
float force_positive(float value) {
    uint32_t bits;
    std::memcpy(&bits, &value, sizeof(bits));
    
    // Побітове І з інвертованою маскою (0x7FFFFFFF) очищає знаковий біт
    bits &= ~SIGN_BIT_MASK;
    
    float result;
    std::memcpy(&result, &bits, sizeof(result));
    return result;
}

int main() {
    float a = 42.5f;
    float b = -13.25f;
    
    // Перевірка знаку
    std::cout << "Is " << a << " negative? " << (is_negative(a) ? "Yes" : "No") << "\n";
    std::cout << "Is " << b << " negative? " << (is_negative(b) ? "Yes" : "No") << "\n";
    
    // Зміна знаку
    std::cout << "\nFlipping sign of " << a << " -> " << flip_sign(a) << "\n";
    std::cout << "Flipping sign of " << b << " -> " << flip_sign(b) << "\n";
    
    // Абсолютне значення (force positive)
    std::cout << "\nAbsolute value of " << a << " -> " << force_positive(a) << "\n";
    std::cout << "Absolute value of " << b << " -> " << force_positive(b) << "\n";
    
    // Демонстрація двох нулів
    float zero_pos = 0.0f;
    float zero_neg = flip_sign(zero_pos); // Створюємо -0.0f
    
    std::cout << "\nPos zero == Neg zero? " << (zero_pos == zero_neg ? "True" : "False") << "\n";
    std::cout << "Is zero_pos negative? " << (is_negative(zero_pos) ? "Yes" : "No") << "\n";
    std::cout << "Is zero_neg negative? " << (is_negative(zero_neg) ? "Yes" : "No") << "\n";
    
    return 0;
}
