#include "hx711_pullout.h"
#include <stdio.h>

#ifndef PLATFORM_HARDWARE_GPIO
/* Симуляційний генератор сигналів тензомосту для демонстраційного середовища */
static int s_sim_step = 0;

static int32_t simulate_hx711_counts(const hx711_pullout_t *sensor) {
    s_sim_step++;
    float simulated_n = 0.0f;

    if (s_sim_step < 10) {
        simulated_n = 0.0f; /* фаза тарування навантаження відсутнє */
    } else if (s_sim_step < 60) {
        /* Лінійне пружне навантаження бобишки до 625 Н */
        simulated_n = (s_sim_step - 10) * 12.5f;
    } else if (s_sim_step < 75) {
        /* Зрив шліців втулки зі стінок отвору */
        float delta = (s_sim_step - 60) * 35.0f;
        simulated_n = 625.0f - delta;
    } else {
        /* Залишковий опір тертя ковзання */
        simulated_n = 100.0f;
    }

    /* Масштабування у відліки АЦП із додаванням зміщення тари */
    int32_t counts = sensor->tare_offset + (int32_t)(simulated_n * sensor->scale_factor);
    /* Апаратний шум тензометричного мосту */
    counts += ((s_sim_step % 5) - 2) * 18;
    return counts;
}
#endif

void hx711_init(hx711_pullout_t *sensor, int sck_pin, int dout_pin, float scale_factor, float ema_alpha) {
    if (!sensor) return;

    sensor->sck_pin = sck_pin;
    sensor->dout_pin = dout_pin;
    sensor->tare_offset = 0;
    sensor->scale_factor = (scale_factor > 0.0001f) ? scale_factor : 412.5f;
    sensor->ema_alpha = (ema_alpha > 0.0f && ema_alpha <= 1.0f) ? ema_alpha : 0.25f;
    sensor->current_force_n = 0.0f;
    sensor->peak_force_n = 0.0f;
}

bool hx711_is_ready(const hx711_pullout_t *sensor) {
    (void)sensor;
#ifdef PLATFORM_HARDWARE_GPIO
    /* На апаратному рівні низький рівень лінії DOUT свідчить про готовність даних */
    return (gpio_get_level(sensor->dout_pin) == 0);
#else
    return true;
#endif
}

int32_t hx711_read_raw(const hx711_pullout_t *sensor) {
#ifdef PLATFORM_HARDWARE_GPIO
    uint32_t raw = 0;

    /* Очікування сигналу готовності АЦП */
    while (!hx711_is_ready(sensor)) {
        /* коротка пауза очікування */
    }

    /* Синхронний біт-бенгінг: 24 тактових імпульси на SCK */
    for (int i = 0; i < 24; i++) {
        gpio_set_level(sensor->sck_pin, 1);
        esp_rom_delay_us(1);
        raw = (raw << 1) | (gpio_get_level(sensor->dout_pin) & 0x01);
        gpio_set_level(sensor->sck_pin, 0);
        esp_rom_delay_us(1);
    }

    /* 25-й імпульс встановлює канал А з підсиленням 128 для наступного циклу */
    gpio_set_level(sensor->sck_pin, 1);
    esp_rom_delay_us(1);
    gpio_set_level(sensor->sck_pin, 0);
    esp_rom_delay_us(1);

    /* Знакове розширення 24-бітного значення у від'ємний діапазон int32_t */
    if (raw & 0x800000) {
        raw |= 0xFF000000;
    }
    return (int32_t)raw;
#else
    return simulate_hx711_counts(sensor);
#endif
}

void hx711_tare(hx711_pullout_t *sensor, uint8_t sample_count) {
    if (!sensor || sample_count == 0) return;

    int64_t accumulator = 0;
    for (uint8_t i = 0; i < sample_count; i++) {
        accumulator += hx711_read_raw(sensor);
    }

    sensor->tare_offset = (int32_t)(accumulator / sample_count);
    sensor->current_force_n = 0.0f;
    sensor->peak_force_n = 0.0f;
}

float hx711_update_force(hx711_pullout_t *sensor) {
    if (!sensor) return 0.0f;

    int32_t raw_counts = hx711_read_raw(sensor);
    int32_t counts_above_tare = raw_counts - sensor->tare_offset;

    float measured_force = (float)counts_above_tare / sensor->scale_factor;
    if (measured_force < 0.0f) {
        measured_force = 0.0f;
    }

    /* Експоненційне згладжування шумів тензомосту: Y[k] = alpha * X[k] + (1 - alpha) * Y[k-1] */
    sensor->current_force_n = (sensor->ema_alpha * measured_force) +
                              ((1.0f - sensor->ema_alpha) * sensor->current_force_n);

    /* Фіксація пікового значення */
    if (sensor->current_force_n > sensor->peak_force_n) {
        sensor->peak_force_n = sensor->current_force_n;
    }

    return sensor->current_force_n;
}

void hx711_reset_peak(hx711_pullout_t *sensor) {
    if (sensor) {
        sensor->peak_force_n = 0.0f;
    }
}

float hx711_get_peak_force(const hx711_pullout_t *sensor) {
    return sensor ? sensor->peak_force_n : 0.0f;
}
