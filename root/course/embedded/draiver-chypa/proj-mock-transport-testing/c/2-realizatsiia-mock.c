// C99: Реалізація емулятора шини та віртуального чипа для Unit-тестів
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>
#include <stdio.h>

#define MOCK_REG_COUNT 128
#define MOCK_MAX_WRITE_LOG 64

// Фіктивні адреси регістрів еталонного акселерометра
#define REG_WHO_AM_I     0x0F
#define REG_CTRL_REG1    0x20
#define REG_CTRL_REG4    0x23
#define REG_STATUS_REG   0x27
#define REG_OUT_X_L      0x28

#define EXPECTED_CHIP_ID 0x33

typedef struct {
    uint8_t reg;
    uint8_t val;
} mock_write_entry_t;

typedef struct {
    uint8_t registers[MOCK_REG_COUNT];
    mock_write_entry_t write_log[MOCK_MAX_WRITE_LOG];
    uint32_t write_count;
    
    // Поля ін'єкції несправностей
    int32_t fail_reads_countdown;
    int32_t fail_writes_countdown;
    bool nack_device_address;
} mock_bus_ctx_t;

// Очищення та скидання стану мока
void mock_bus_reset(mock_bus_ctx_t *mock) {
    memset(mock->registers, 0, sizeof(mock->registers));
    mock->write_count = 0;
    mock->fail_reads_countdown = 0;
    mock->fail_writes_countdown = 0;
    mock->nack_device_address = false;
    
    // Встановлення заводського ідентифікатора за замовчуванням
    mock->registers[REG_WHO_AM_I] = EXPECTED_CHIP_ID;
}

// Запис сирих 16-бітних відліків у регістри даних віртуального датчика
void mock_set_raw_xyz(mock_bus_ctx_t *mock, int16_t x, int16_t y, int16_t z) {
    mock->registers[REG_OUT_X_L + 0] = (uint8_t)(x & 0xFF);
    mock->registers[REG_OUT_X_L + 1] = (uint8_t)((x >> 8) & 0xFF);
    mock->registers[REG_OUT_X_L + 2] = (uint8_t)(y & 0xFF);
    mock->registers[REG_OUT_X_L + 3] = (uint8_t)((y >> 8) & 0xFF);
    mock->registers[REG_OUT_X_L + 4] = (uint8_t)(z & 0xFF);
    mock->registers[REG_OUT_X_L + 5] = (uint8_t)((z >> 8) & 0xFF);
    
    // Встановлення прапорця готовності нових даних ZYXDA (біт 3 у STATUS_REG)
    mock->registers[REG_STATUS_REG] |= (1U << 3);
}

// Функція читання шини для драйвера
int32_t mock_bus_read(void *user_ctx, uint8_t reg_addr, uint8_t *data, uint16_t len) {
    mock_bus_ctx_t *mock = (mock_bus_ctx_t *)user_ctx;
    if (mock->nack_device_address) return -2; // Симуляція помилки адресації
    if (mock->fail_reads_countdown > 0) {
        mock->fail_reads_countdown--;
        return -2; // Симуляція апаратного збою
    }
    
    for (uint16_t i = 0; i < len; ++i) {
        uint8_t current_reg = (uint8_t)((reg_addr + i) & 0x7F);
        data[i] = mock->registers[current_reg];
    }
    return 0;
}

// Функція запису шини для драйвера
int32_t mock_bus_write(void *user_ctx, uint8_t reg_addr, const uint8_t *data, uint16_t len) {
    mock_bus_ctx_t *mock = (mock_bus_ctx_t *)user_ctx;
    if (mock->nack_device_address) return -2;
    if (mock->fail_writes_countdown > 0) {
        mock->fail_writes_countdown--;
        return -2;
    }
    
    for (uint16_t i = 0; i < len; ++i) {
        uint8_t current_reg = (uint8_t)((reg_addr + i) & 0x7F);
        mock->registers[current_reg] = data[i];
        
        if (mock->write_count < MOCK_MAX_WRITE_LOG) {
            mock->write_log[mock->write_count].reg = current_reg;
            mock->write_log[mock->write_count].val = data[i];
            mock->write_count++;
        }
    }
    return 0;
}

void mock_delay_ms(uint32_t ms) {
    // В юніт-тестах затримка виконується миттєво для максимальної швидкості
    (void)ms;
}
