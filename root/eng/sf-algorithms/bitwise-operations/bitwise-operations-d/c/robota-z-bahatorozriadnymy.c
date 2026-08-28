#include <stdint.h>
#include <stdbool.h>

#define FIELD_OFFSET 4
#define FIELD_WIDTH  4
#define FIELD_MASK   (((1U << FIELD_WIDTH) - 1) << FIELD_OFFSET)

// Витягти значення поля (0..15) з регістра
uint32_t get_field(uint32_t reg) {
    return (reg & FIELD_MASK) >> FIELD_OFFSET;
}

// Записати нове значення в поле регістра
uint32_t set_field(uint32_t reg, uint32_t value) {
    // 1. Очистити біти поля в регістрі
    // 2. Вставити нове значення, зсунуте на позицію поля
    return (reg & ~FIELD_MASK) | ((value << FIELD_OFFSET) & FIELD_MASK);
}
