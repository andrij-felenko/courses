#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include "esp_system.h"
#include "driver/adc.h"
#include "driver/ledc.h"

#define ADC_CHANNEL         ADC1_CHANNEL_6 // GPIO34
#define ADC_MAX_VAL         4095.0f
#define V_REF               3.3f
#define SHUNT_RESISTOR_OHM  0.5f
#define AMP_GAIN            10.0f
#define SAMPLE_WINDOW       32

#define DRY_RUN_I_THRESH_A  0.040f // 40 мА поріг сухого ходу
#define STALL_I_THRESH_A    0.350f // 350 мА поріг заклинення
#define MAX_COIL_TEMP_C     85.0f  // Гранична температура
#define R0_COIL_OHM         12.0f  // Опір обмотки при 20 °C
#define ALPHA_COPPER        0.00393f

typedef enum {
    PUMP_STATE_INIT,
    PUMP_STATE_STARTUP,
    PUMP_STATE_NORMAL,
    PUMP_STATE_FAULT_DRY_RUN,
    PUMP_STATE_FAULT_OVERHEAT,
    PUMP_STATE_COOLDOWN
} pump_state_t;

typedef struct {
    pump_state_t state;
    float current_samples[SAMPLE_WINDOW];
    size_t sample_idx;
    float i_rms;
    float estimated_temp_c;
    uint32_t state_timer_ms;
    uint32_t debounce_counter;
} micropump_protection_t;

static micropump_protection_t g_pump_dev = {0};

void micropump_hw_init(void) {
    adc1_config_width(ADC_WIDTH_BIT_12);
    adc1_config_channel_atten(ADC_CHANNEL, ADC_ATTEN_DB_11);
}

float micropump_read_instant_current(void) {
    int raw = adc1_get_raw(ADC_CHANNEL);
    float voltage = ((float)raw / ADC_MAX_VAL) * V_REF;
    // Струм = напруга / (підсилення * шунт)
    return voltage / (AMP_GAIN * SHUNT_RESISTOR_OHM);
}

void micropump_update_rms(micropump_protection_t *dev, float new_current) {
    dev->current_samples[dev->sample_idx] = new_current;
    dev->sample_idx = (dev->sample_idx + 1) % SAMPLE_WINDOW;

    float sum_sq = 0.0f;
    for (size_t i = 0; i < SAMPLE_WINDOW; i++) {
        sum_sq += dev->current_samples[i] * dev->current_samples[i];
    }
    dev->i_rms = sqrtf(sum_sq / (float)SAMPLE_WINDOW);
}

// Оцінка температури обмотки за зростанням опору
float micropump_estimate_temperature(float measured_r_coil) {
    if (measured_r_coil <= R0_COIL_OHM) return 20.0f;
    return 20.0f + (measured_r_coil - R0_COIL_OHM) / (R0_COIL_OHM * ALPHA_COPPER);
}

void micropump_process_protection_tick(micropump_protection_t *dev, float dt_ms) {
    float i_inst = micropump_read_instant_current();
    micropump_update_rms(dev, i_inst);
    dev->state_timer_ms += (uint32_t)dt_ms;

    switch (dev->state) {
        case PUMP_STATE_INIT:
            dev->state = PUMP_STATE_STARTUP;
            dev->state_timer_ms = 0;
            break;

        case PUMP_STATE_STARTUP:
            // Ігноруємо пускові сплески струму протягом 100 мс
            if (dev->state_timer_ms > 100) {
                dev->state = PUMP_STATE_NORMAL;
            }
            break;

        case PUMP_STATE_NORMAL:
            // Перевірка сухого ходу
            if (dev->i_rms < DRY_RUN_I_THRESH_A) {
                dev->debounce_counter++;
                if (dev->debounce_counter > 10) { // 10 послідовних відліків
                    dev->state = PUMP_STATE_FAULT_DRY_RUN;
                    printf("АВАРІЯ: Виявлено сухий хід! I_rms = %.3f A\n", dev->i_rms);
                }
            } else {
                dev->debounce_counter = 0;
            }

            // Оцінка температури та перевірка перегріву
            if (dev->estimated_temp_c > MAX_COIL_TEMP_C) {
                dev->state = PUMP_STATE_FAULT_OVERHEAT;
                printf("АВАРІЯ: Перегрів обмотки! T = %.1f °C\n", dev->estimated_temp_c);
            }
            break;

        case PUMP_STATE_FAULT_DRY_RUN:
        case PUMP_STATE_FAULT_OVERHEAT:
            // Аварійне знеструмлення приводу
            dev->state = PUMP_STATE_COOLDOWN;
            dev->state_timer_ms = 0;
            break;

        case PUMP_STATE_COOLDOWN:
            // Пауза 5 секунд на охолодження перед повторною спробою
            if (dev->state_timer_ms > 5000) {
                dev->state = PUMP_STATE_STARTUP;
                dev->state_timer_ms = 0;
                printf("Спроба повторного запуску після охолодження...\n");
            }
            break;
    }
}
