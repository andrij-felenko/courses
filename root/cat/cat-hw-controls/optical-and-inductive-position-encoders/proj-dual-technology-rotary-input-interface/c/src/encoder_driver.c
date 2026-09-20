#include "encoder_driver.h"
#include <math.h>

// Константне перетворення градусів
#define FULL_CIRCLE_DEG 360.0f

void yoke_system_init(yoke_position_system_t *sys, uint32_t qei_ppr, float rvdt_sensitivity, float max_diff_deg, uint32_t timeout_ms) {
    if (!sys) return;

    // Налаштування каналу QEI
    sys->qei.ppr = (qei_ppr > 0) ? qei_ppr : 4096;
    sys->qei.pulse_count = 0;
    sys->qei.current_angle_deg = 0.0f;
    sys->qei.index_found = false;

    // Налаштування каналу RVDT
    sys->rvdt.sensitivity_mv_per_deg = (rvdt_sensitivity > 0.0f) ? rvdt_sensitivity : 10.0f;
    sys->rvdt.zero_offset_deg = 0.0f;
    sys->rvdt.current_angle_deg = 0.0f;
    sys->rvdt.signal_valid = true;
    for (int i = 0; i < RVDT_DMA_BUFFER_SIZE; ++i) {
        sys->rvdt.adc_dma_buffer[i] = 0;
    }

    // Налаштування модуля порівняння
    sys->comparator.max_allowed_diff_deg = max_diff_deg;
    sys->comparator.discrepancy_timeout_ms = timeout_ms;
    sys->comparator.discrepancy_start_ms = 0;
    sys->comparator.in_discrepancy = false;
    sys->comparator.status = COMPARE_OK;

    sys->valid_position_deg = 0.0f;
    sys->system_healthy = true;
}

void yoke_update_qei(yoke_position_system_t *sys, int32_t raw_pulses, bool index_pin) {
    if (!sys) return;

    sys->qei.pulse_count = raw_pulses;
    if (index_pin) {
        sys->qei.index_found = true;
    }

    // Обчислення кута в діапазоні -180... +180 градусів
    float raw_angle = ((float)(raw_pulses % (int32_t)sys->qei.ppr) / (float)sys->qei.ppr) * FULL_CIRCLE_DEG;
    if (raw_angle > 180.0f) {
        raw_angle -= FULL_CIRCLE_DEG;
    } else if (raw_angle < -180.0f) {
        raw_angle += FULL_CIRCLE_DEG;
    }

    sys->qei.current_angle_deg = raw_angle;
}

void yoke_update_rvdt(yoke_position_system_t *sys, const uint16_t *adc_samples, uint16_t count) {
    if (!sys || !adc_samples || count == 0) return;

    // Обчислення середнього значення напруги огинаючої RVDT із буфера DMA
    uint32_t sum = 0;
    uint16_t sample_count = (count < RVDT_DMA_BUFFER_SIZE) ? count : RVDT_DMA_BUFFER_SIZE;
    
    for (uint16_t i = 0; i < sample_count; ++i) {
        sys->rvdt.adc_dma_buffer[i] = adc_samples[i];
        sum += adc_samples[i];
    }

    float avg_adc = (float)sum / (float)sample_count;
    
    // Перетворення напруги АЦП (3.3В / 12-біт) у кут повороту RVDT
    float voltage_mv = (avg_adc / 4095.0f) * 3300.0f;
    
    // Віднімаємо опорну точку 1.65В (1650 мВ) для виявлення знака кута
    float net_voltage = voltage_mv - 1650.0f;
    float calculated_angle = net_voltage / sys->rvdt.sensitivity_mv_per_deg;

    // Перевірка допустимого апаратного діапазону сигналу RVDT (наприклад, -60... +60 град)
    if (calculated_angle > 90.0f || calculated_angle < -90.0f) {
        sys->rvdt.signal_valid = false;
    } else {
        sys->rvdt.signal_valid = true;
        sys->rvdt.current_angle_deg = calculated_angle - sys->rvdt.zero_offset_deg;
    }
}

compare_status_t yoke_process_cycle(yoke_position_system_t *sys, uint32_t current_time_ms) {
    if (!sys) return COMPARE_ERROR_HARDWARE;

    // 1. Перевірка апаратного здоров'я каналу RVDT
    if (!sys->rvdt.signal_valid) {
        sys->comparator.status = COMPARE_ERROR_HARDWARE;
        sys->system_healthy = false;
        return COMPARE_ERROR_HARDWARE;
    }

    // 2. Обчислення абсолютної різниці між координатами QEI та RVDT
    float diff = fabsf(sys->qei.current_angle_deg - sys->rvdt.current_angle_deg);

    // 3. Логіка виявлення розбіжності каналів (Cross-Comparison)
    if (diff > sys->comparator.max_allowed_diff_deg) {
        if (!sys->comparator.in_discrepancy) {
            sys->comparator.in_discrepancy = true;
            sys->comparator.discrepancy_start_ms = current_time_ms;
            sys->comparator.status = COMPARE_WARNING_DISCREPANCY;
        } else {
            if (current_time_ms - sys->comparator.discrepancy_start_ms > sys->comparator.discrepancy_timeout_ms) {
                sys->comparator.status = COMPARE_ERROR_DISCREPANCY;
                sys->system_healthy = false;
            }
        }
    } else {
        // Узгоджений стан каналів
        sys->comparator.in_discrepancy = false;
        sys->comparator.discrepancy_start_ms = 0;
        
        if (sys->comparator.status != COMPARE_ERROR_DISCREPANCY && 
            sys->comparator.status != COMPARE_ERROR_HARDWARE) {
            sys->comparator.status = COMPARE_OK;
            sys->system_healthy = true;
            // Усереднення координат високої точності при нормі
            sys->valid_position_deg = (sys->qei.current_angle_deg + sys->rvdt.current_angle_deg) * 0.5f;
        }
    }

    return sys->comparator.status;
}

bool yoke_reset_fault(yoke_position_system_t *sys) {
    if (!sys) return false;

    float diff = fabsf(sys->qei.current_angle_deg - sys->rvdt.current_angle_deg);
    if (diff <= sys->comparator.max_allowed_diff_deg && sys->rvdt.signal_valid) {
        sys->comparator.status = COMPARE_OK;
        sys->comparator.in_discrepancy = false;
        sys->system_healthy = true;
        return true;
    }
    return false;
}
