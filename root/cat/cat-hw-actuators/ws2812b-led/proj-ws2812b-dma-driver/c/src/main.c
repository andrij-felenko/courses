#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "ws2812b.h"

/**
 * @file main.c
 * @brief Приклад використання C-драйвера WS2812B з асинхронною передачею через DMA.
 *
 * Демонструє створення та ініціалізацію світлодіодної стрічки, створення динамічних
 * світлових ефектів (плавна веселка, біжуча біла хвиля, пульсація яскравістю)
 * та обробку переривань DMA без залучення блокуючих затримок CPU.
 */

#define LED_STRIP_SIZE  30U

/* Імітація апаратного регістру порівняння TIM PWM (CCR1) */
static volatile uint32_t s_mock_tim_ccr = 0;

/* Буфер кадру кольорів пікселів стрічки у оперативній пам'яті */
static ws2812b_color_t s_pixel_framebuf[LED_STRIP_SIZE];

/* Екземпляр драйвера стрічки */
static ws2812b_t s_strip;

/**
 * @brief Генерація ефекту "Веселка" (Rainbow Chase) уздовж усієї стрічки.
 * 
 * @param ws Вказівник на драйвер стрічки.
 * @param frame Індекс поточного кадру анімації.
 */
static void effect_rainbow(ws2812b_t *ws, uint16_t frame) {
    for (uint16_t i = 0; i < ws->num_leds; i++) {
        uint16_t hue = (frame * 5 + i * (360 / ws->num_leds)) % 360;
        ws2812b_set_pixel_hsv(ws, i, hue, 255, 200);
    }
}

/**
 * @brief Генерація ефекту "Біжуча хвиля" (Running Light Pulse).
 *
 * @param ws Вказівник на драйвер стрічки.
 * @param frame Індекс поточного кадру анімації.
 */
static void effect_chase_wave(ws2812b_t *ws, uint16_t frame) {
    ws2812b_clear(ws);
    uint16_t head = frame % ws->num_leds;

    for (uint8_t tail = 0; tail < 5; tail++) {
        int16_t pos = (int16_t)head - tail;
        if (pos >= 0 && pos < (int16_t)ws->num_leds) {
            uint8_t brightness = 255 >> tail;
            ws2812b_set_pixel_rgb(ws, (uint16_t)pos, brightness, brightness / 2, 0);
        }
    }
}

/**
 * @brief Генерація ефекту "Дихання" (Breathing Pulse).
 *
 * @param ws Вказівник на драйвер стрічки.
 * @param frame Індекс поточного кадру анімації.
 */
static void effect_breathing(ws2812b_t *ws, uint16_t frame) {
    uint8_t val = (uint8_t)((frame % 256 < 128) ? (frame % 128 * 2) : (255 - (frame % 128 * 2)));

    for (uint16_t i = 0; i < ws->num_leds; i++) {
        /* Синя пульсація з регульованою яскравістю */
        ws2812b_set_pixel_hsv(ws, i, 220, 255, val);
    }
}

/**
 * @brief Симуляція апаратної передачі DMA та викликів переривань HT/TC.
 * 
 * У реальній системі це виконується периферійним контролером DMA в фоні.
 */
static void simulate_dma_hardware_transfer(ws2812b_t *ws) {
    if (!ws2812b_is_busy(ws)) {
        return;
    }

    /* Симуляція серії циклів DMA transfer з генерацією HT та TC переривань */
    while (ws2812b_is_busy(ws)) {
        /* Симуляція переривання Half Transfer (HT) */
        ws2812b_dma_ht_isr(ws);

        /* Симуляція переривання Transfer Complete (TC) */
        ws2812b_dma_tc_isr(ws);
    }
}

int main(void) {
    printf("=== Ініціалізація C-драйвера WS2812B (TIM + DMA Circular Mode) ===\n");

    /* 1. Ініціалізація драйвера стрічки */
    ws2812b_err_t err = ws2812b_init(&s_strip, s_pixel_framebuf, LED_STRIP_SIZE, &s_mock_tim_ccr);
    if (err != WS2812B_OK) {
        printf("Помилка ініціалізації драйвера: %d\n", err);
        return -1;
    }

    printf("Драйвер успішно ініціалізовано. Кількість світлодіодів: %u\n", s_strip.num_leds);
    printf("Розмір подвійного буфера DMA: %u відліків (24 біти HT + 24 біти TC)\n\n", WS2812B_DMA_BUFFER_SIZE);

    /* 2. Демонстрація ефекту 1: Веселка (Rainbow) */
    printf("--- Запуск ефекту: Веселка ---\n");
    for (uint16_t frame = 0; frame < 5; frame++) {
        effect_rainbow(&s_strip, frame);

        /* Запуск асинхронного неблокуючого оновлення стрічки */
        err = ws2812b_update(&s_strip);
        if (err == WS2812B_OK) {
            printf("[Кадр %u] Оновлення стрічки запущено через DMA (State: SENDING)...\n", frame);
            simulate_dma_hardware_transfer(&s_strip);
            printf("[Кадр %u] Оновлення завершено. (State: IDLE)\n", frame);
        } else {
            printf("[Кадр %u] Драйвер зайнятий!\n", frame);
        }
    }

    /* 3. Демонстрація ефекту 2: Біжуча хвиля */
    printf("\n--- Запуск ефекту: Біжуча хвиля ---\n");
    for (uint16_t frame = 0; frame < 5; frame++) {
        effect_chase_wave(&s_strip, frame);

        err = ws2812b_update(&s_strip);
        if (err == WS2812B_OK) {
            printf("[Кадр %u] Оновлення стрічки запущено через DMA...\n", frame);
            simulate_dma_hardware_transfer(&s_strip);
            printf("[Кадр %u] Оновлення завершено.\n", frame);
        }
    }

    /* 4. Демонстрація ефекту 3: Пульсація */
    printf("\n--- Запуск ефекту: Дихання ---\n");
    for (uint16_t frame = 0; frame < 5; frame++) {
        effect_breathing(&s_strip, frame);

        err = ws2812b_update(&s_strip);
        if (err == WS2812B_OK) {
            printf("[Кадр %u] Оновлення стрічки запущено через DMA...\n", frame);
            simulate_dma_hardware_transfer(&s_strip);
            printf("[Кадр %u] Оновлення завершено.\n", frame);
        }
    }

    printf("\n=== Завершення роботи пристрою ===\n");
    return 0;
}
