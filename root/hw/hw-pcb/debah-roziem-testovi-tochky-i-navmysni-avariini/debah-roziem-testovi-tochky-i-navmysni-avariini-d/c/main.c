#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#define POWER_RAIL_COUNT 4
#define MAX_I2C_DEVICES  128

typedef struct {
    const char *name;
    uint32_t adc_channel;
    float expected_voltage;
    float tolerance_percent;
} PowerRailSpec;

typedef struct {
    float measured_voltage;
    bool in_tolerance;
} PowerRailResult;

typedef struct {
    uint8_t address;
    bool acknowledged;
} I2CDeviceStatus;

typedef struct {
    uint32_t passed_rails;
    uint32_t failed_rails;
    uint32_t detected_i2c_nodes;
    bool gpio_loopback_ok;
} DiagnosticSummary;

/* Специфікація допустимих параметрів шин живлення плати */
static const PowerRailSpec g_power_specs[POWER_RAIL_COUNT] = {
    { "+3.3V_SYS",  0, 3.30f, 5.0f },
    { "+1.8V_CORE", 1, 1.80f, 4.0f },
    { "+3.3V_VDDA", 2, 3.30f, 2.5f },
    { "+12V_INPUT", 3, 12.00f, 10.0f }
};

/* Апаратні абстракції для взаємодії з периферією мікроконтролера */
extern uint16_t hal_adc_read_raw(uint32_t channel);
extern bool hal_i2c_ping_address(uint8_t addr_7bit);
extern void hal_gpio_write_pin(uint32_t pin_idx, bool state);
extern bool hal_gpio_read_pin(uint32_t pin_idx);
extern void hal_uart_send_string(const char *str);

/* Перерахунок коду АЦП у напругу з урахуванням дільника */
static float calculate_voltage(uint32_t channel, uint16_t raw_adc) {
    const float v_ref = 3.30f;
    const float adc_max = 4095.0f; /* 12-розрядний АЦП */
    float v_pin = ((float)raw_adc / adc_max) * v_ref;

    /* Коефіцієнти масштабування резистивних дільників */
    if (channel == 3) {
        return v_pin * ( (100.0f + 20.0f) / 20.0f ); /* Дільник 100k/20k для 12V */
    }
    return v_pin;
}

/* Тестування всіх шин живлення плати */
void run_power_rail_audit(PowerRailResult *results, DiagnosticSummary *summary) {
    char log_buf[128];
    summary->passed_rails = 0;
    summary->failed_rails = 0;

    hal_uart_send_string("\r\n=== [1] АУДИТ ШИН ЖИВЛЕННЯ ТА ТЕСТОВИХ ТОЧОК ===\r\n");

    for (uint32_t i = 0; i < POWER_RAIL_COUNT; ++i) {
        uint16_t raw = hal_adc_read_raw(g_power_specs[i].adc_channel);
        float v_meas = calculate_voltage(g_power_specs[i].adc_channel, raw);
        results[i].measured_voltage = v_meas;

        float delta = v_meas - g_power_specs[i].expected_voltage;
        if (delta < 0.0f) delta = -delta;
        float max_allowed_delta = g_power_specs[i].expected_voltage * (g_power_specs[i].tolerance_percent / 100.0f);

        if (delta <= max_allowed_delta) {
            results[i].in_tolerance = true;
            summary->passed_rails++;
            snprintf(log_buf, sizeof(log_buf), "  [PASS] %-11s : %.3f В (Очік: %.2f В +-%.1f%%)\r\n",
                     g_power_specs[i].name, v_meas, g_power_specs[i].expected_voltage, g_power_specs[i].tolerance_percent);
        } else {
            results[i].in_tolerance = false;
            summary->failed_rails++;
            snprintf(log_buf, sizeof(log_buf), "  [FAIL] %-11s : %.3f В (ПОХИБКА! Очік: %.2f В)\r\n",
                     g_power_specs[i].name, v_meas, g_power_specs[i].expected_voltage);
        }
        hal_uart_send_string(log_buf);
    }
}

/* Сканування шини I2C для виявлення змонтованих датчиків */
uint32_t run_i2c_bus_scan(I2CDeviceStatus *found_devices) {
    char log_buf[64];
    uint32_t count = 0;

    hal_uart_send_string("\r\n=== [2] СКАheaderНУВАННЯ ШИНИ I2C (0x08 - 0x77) ===\r\n");

    for (uint8_t addr = 0x08; addr <= 0x77; ++addr) {
        if (hal_i2c_ping_address(addr)) {
            found_devices[count].address = addr;
            found_devices[count].acknowledged = true;
            snprintf(log_buf, sizeof(log_buf), "  [FOUND] Пристрій I2C за адресою: 0x%02X (ACK)\r\n", addr);
            hal_uart_send_string(log_buf);
            count++;
        }
    }
    if (count == 0) {
        hal_uart_send_string("  [WARN] Жодного I2C-пристрою не знайдено на шині!\r\n");
    }
    return count;
}

/* Побітовий стрес-тест цифрових ліній зв'язку (Walking Ones Test) */
bool run_gpio_walking_test(uint32_t out_pin, uint32_t in_pin) {
    hal_uart_send_string("\r\n=== [3] ТЕСТ ЦІЛІСНОСТІ ЛІНІЙ GPIO (LOOPBACK) ===\r\n");

    /* Тест нульового рівня */
    hal_gpio_write_pin(out_pin, false);
    if (hal_gpio_read_pin(in_pin) != false) {
        hal_uart_send_string("  [FAIL] Замикання лінії на VCC або обрив підтяжки!\r\n");
        return false;
    }

    /* Тест одиничного рівня */
    hal_gpio_write_pin(out_pin, true);
    if (hal_gpio_read_pin(in_pin) != true) {
        hal_uart_send_string("  [FAIL] Замикання лінії на GND або обрив провідника!\r\n");
        return false;
    }

    hal_uart_send_string("  [PASS] Лінії GPIO успішно пройшли динамічний тест Loopback.\r\n");
    return true;
}
