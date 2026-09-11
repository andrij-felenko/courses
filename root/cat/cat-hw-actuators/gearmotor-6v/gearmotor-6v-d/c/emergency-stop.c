#include <stdio.h>
#include <stdbool.h>
#include "esp_timer.h"
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "esp_adc/adc_oneshot.h"

#define PIN_MOTOR_DIR1       GPIO_NUM_18
#define PIN_MOTOR_DIR2       GPIO_NUM_19
#define PIN_MOTOR_PWM        GPIO_NUM_21
#define ADC_CURRENT_CHANNEL  ADC_CHANNEL_6 // Вивід GPIO34 для модуля ADC1

#define SHUNT_RESISTANCE_OHM 0.1f
#define ADC_FULL_SCALE_VOLTS 3.3f
#define ADC_MAX_READING      4095.0f
#define STALL_CURRENT_AMPS   1.2f
#define STALL_TIMEOUT_US     (150 * 1000) // 150 мс у мікросекундах

typedef enum {
    DRIVER_STATE_STOPPED,
    DRIVER_STATE_RUNNING,
    DRIVER_STATE_FAULT_STALL
} driver_state_t;

static driver_state_t g_driver_state = DRIVER_STATE_STOPPED;
static int64_t g_overcurrent_start_us = 0;
static bool g_is_overcurrent = false;
static adc_oneshot_unit_handle_t g_adc_handle;

// Аварійне зняття ШІМ та знеструмлення виходів моста
void emergency_stop(void) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, 0);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
    gpio_set_level(PIN_MOTOR_DIR1, 0);
    gpio_set_level(PIN_MOTOR_DIR2, 0);
    g_driver_state = DRIVER_STATE_FAULT_STALL;
}

// Вимірювання струму двигуна через оцифрування падіння напруги на шунті
float get_motor_current(void) {
    int raw_val = 0;
    adc_oneshot_read(g_adc_handle, ADC_CURRENT_CHANNEL, &raw_val);
    float voltage = ((float)raw_val * ADC_FULL_SCALE_VOLTS) / ADC_MAX_READING;
    return voltage / SHUNT_RESISTANCE_OHM;
}

// Неблокуюча перевірка таймауту перевантаження двигуна
void process_current_protection(void) {
    if (g_driver_state != DRIVER_STATE_RUNNING) {
        return;
    }

    float current = get_motor_current();
    int64_t current_time_us = esp_timer_get_time();

    if (current >= STALL_CURRENT_AMPS) {
        if (!g_is_overcurrent) {
            g_is_overcurrent = true;
            g_overcurrent_start_us = current_time_us;
        } else if (current_time_us - g_overcurrent_start_us >= STALL_TIMEOUT_US) {
            // Перевищено критичний таймаут блокування вала
            emergency_stop();
        }
    } else {
        g_is_overcurrent = false;
    }
}
