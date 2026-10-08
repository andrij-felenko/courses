#include <stdint.h>
#include <stdbool.h>

// Структура для збереження телеметрії RDC
typedef struct {
    uint16_t raw_angle;
    int16_t  raw_velocity;
    uint8_t  fault_code;
} rdc_data_t;

// Зчитування 16-бітного кута та швидкості через SPI
bool rdc_read_telemetry(rdc_data_t *dest) {
    uint8_t tx_buf[4] = {0x80, 0x00, 0x00, 0x00}; // Команда зчитування кута та швидкості
    uint8_t rx_buf[4] = {0};

    // Активація вибору мікросхеми CS (Active LOW)
    gpio_set_level(GPIO_RDC_CS, 0);

    // Передача командного байта та прийом даних по SPI
    spi_transfer_bytes(tx_buf, rx_buf, 4);

    // Деактивація CS
    gpio_set_level(GPIO_RDC_CS, 1);

    // Збирання 16-бітного значення кута з двох байтів
    dest->raw_angle = ((uint16_t)rx_buf[0] << 8) | rx_buf[1];
    
    // Збирання 16-бітного значення швидкості
    dest->raw_velocity = ((int16_t)rx_buf[2] << 8) | rx_buf[3];

    // Перевірка прапора помилки в молодших бітах
    if (rx_buf[3] & 0x01) {
        dest->fault_code = rdc_read_fault_register();
        return false;
    }

    dest->fault_code = 0;
    return true;
}
