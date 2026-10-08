#include <stdint.h>
#include <stdbool.h>

// Перетворення двійкового числа в рефлексивний код Ґрея
uint32_t binary_to_gray(uint32_t binary) {
    return binary ^ (binary >> 1);
}

// Швидке паралельне логарифмічне декодування 32-бітного коду Ґрея в двійковий формат
uint32_t gray_to_binary32(uint32_t gray) {
    gray ^= (gray >> 1);
    gray ^= (gray >> 2);
    gray ^= (gray >> 4);
    gray ^= (gray >> 8);
    gray ^= (gray >> 16);
    return gray;
}

// Декодування урізаного коду Ґрея (Excess Gray code) для некратних роздільностей
// gray: зчитаний код з енкодера
// resolution: парна роздільність (наприклад, 360 або 1000)
// bit_depth: кількість бітів диска k (наприклад, 9 для 360)
int32_t excess_gray_to_binary(uint32_t gray, uint32_t resolution, uint8_t bit_depth) {
    uint32_t total_states = 1U << bit_depth;
    uint32_t offset = (total_states - resolution) / 2;
    
    // 1. Декодуємо код Ґрея у зсунутий двійковий індекс
    uint32_t shifted_binary = gray_to_binary32(gray);
    
    // 2. Віднімаємо симетричний зсув для отримання реального кутового відліку
    if (shifted_binary < offset || shifted_binary >= (offset + resolution)) {
        return -1; // Помилка: зчитаний код знаходиться поза межами робочого діапазону
    }
    
    return (int32_t)(shifted_binary - offset);
}
