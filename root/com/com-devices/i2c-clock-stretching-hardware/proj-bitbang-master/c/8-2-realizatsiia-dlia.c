// Реалізація HAL для ESP32 мовою C
#include "soc/gpio_struct.h"
#include "esp_timer.h"

#define PIN_SCL 22
#define PIN_SDA 21

void esp32_scl_low(void) {
    GPIO.out_w1tc = (1ULL << PIN_SCL);
}

void esp32_scl_high_z(void) {
    GPIO.out_w1ts = (1ULL << PIN_SCL);
}

bool esp32_read_scl(void) {
    return (GPIO.in >> PIN_SCL) & 0x1;
}

void esp32_sda_low(void) {
    GPIO.out_w1tc = (1ULL << PIN_SDA);
}

void esp32_sda_high_z(void) {
    GPIO.out_w1ts = (1ULL << PIN_SDA);
}

bool esp32_read_sda(void) {
    return (GPIO.in >> PIN_SDA) & 0x1;
}

uint32_t esp32_get_us(void) {
    return (uint32_t)esp_timer_get_time();
}
