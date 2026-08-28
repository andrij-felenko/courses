#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Безпечне ділення за стелею для 32-бітних беззнакових чисел
uint32_t safe_ceil_div_u32(uint32_t a, uint32_t b) {
    if (b == 0) return 0; // Захист від ділення на нуль
    if (a == 0) return 0;
    
    // Формула без ризику переповнення a + b - 1
    return 1U + (a - 1U) / b;
}

// Альтернативний безрозгалужений варіант через остачу
uint32_t safe_ceil_div_branchless(uint32_t a, uint32_t b) {
    if (b == 0) return 0;
    return (a / b) + ((a % b) != 0U);
}
