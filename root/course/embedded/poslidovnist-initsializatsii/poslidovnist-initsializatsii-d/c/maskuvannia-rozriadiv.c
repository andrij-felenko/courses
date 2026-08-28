#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t reg_addr;
    uint8_t target_val;
    uint8_t care_mask;  /* Маска лише R/W бітів конфігурації */
} reg_verify_entry_t;

/* Безпечний запис конфігурації з верифікацією Read-Back */
bool write_and_verify_register(uint8_t dev_addr, const reg_verify_entry_t *entry) {
    /* 1. Записуємо значення по шині */
    if (i2c_write_reg(dev_addr, entry->reg_addr, entry->target_val) != 0) {
        return false; /* Збій на рівні фізичного зв'язку */
    }

    /* 2. Зчитуємо значення назад із мікросхеми */
    uint8_t read_val = 0;
    if (i2c_read_reg(dev_addr, entry->reg_addr, &read_val) != 0) {
        return false;
    }

    /* 3. Порівнюємо значення ТІЛЬКИ у значущих бітах */
    uint8_t target_masked = entry->target_val & entry->care_mask;
    uint8_t read_masked = read_val & entry->care_mask;

    return (target_masked == read_masked);
}
