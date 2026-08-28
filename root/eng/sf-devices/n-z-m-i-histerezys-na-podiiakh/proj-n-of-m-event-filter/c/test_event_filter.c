/**
 * @file test_event_filter.c
 * @brief Верифікаційний стенд фільтрації N-з-M на C99
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <time.h>
#include "event_filter.h"

/* Генератор шуму Бернуллі */
static bool generate_bernoulli_noise(double error_probability) {
    double r = (double)rand() / (double)RAND_MAX;
    return r < error_probability;
}

/* Симуляція механічного брязкоту кнопки */
static void run_contact_bounce_test(void) {
    event_filter_config_t cfg = {
        .m_window = 16,
        .n_on = 12,
        .n_off = 4,
        .max_dwell_samples = 1000
    };

    event_filter_fast32_t filter;
    event_filter_fast32_init(&filter, &cfg, false);

    printf("[TEST 1] Тестування придушення механічного брязкоту...\n");

    /* Фаза 1: Спокій (100 нулів із 5% шумом) */
    for (int i = 0; i < 100; i++) {
        bool noise_bit = generate_bernoulli_noise(0.05);
        bool state = event_filter_fast32_update(&filter, noise_bit);
        assert(state == false && "Помилка: хибне спрацьовування в стані спокою!");
    }

    /* Фаза 2: Брязкіт замикання (20 тактів із чергуванням 0 і 1) */
    bool bounce_pattern[20] = {
        1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1
    };
    for (int i = 0; i < 20; i++) {
        event_filter_fast32_update(&filter, bounce_pattern[i]);
    }

    /* Фаза 3: Стабільне натискання (50 одиниць із поодинокими нульовими провалами 5%) */
    for (int i = 0; i < 50; i++) {
        bool signal_bit = !generate_bernoulli_noise(0.05);
        bool state = event_filter_fast32_update(&filter, signal_bit);
        assert(state == true && "Помилка: сигнал втрачено через шум утримання!");
    }

    printf(" -> Пройдено успішно: брязкіт придушено, валідний сигнал утримано.\n");
}

/* Статистичний тест Монте-Карло: 10 мільйонів відліків */
static void run_monte_carlo_validation(void) {
    const uint32_t TOTAL_SAMPLES = 10000000U; /* 10^7 відліків */
    const double NOISE_FLOOR = 0.05;           /* 5% білий шум */

    event_filter_config_t cfg = {
        .m_window = 8,
        .n_on = 6,
        .n_off = 2,
        .max_dwell_samples = 0
    };

    event_filter_fast32_t filter;
    event_filter_fast32_init(&filter, &cfg, false);

    printf("[TEST 2] Монте-Карло симуляція на 10^7 відліках (p = 0.05)...\n");

    uint32_t false_positives = 0;
    for (uint32_t i = 0; i < TOTAL_SAMPLES; i++) {
        bool noise_sample = generate_bernoulli_noise(NOISE_FLOOR);
        bool filtered = event_filter_fast32_update(&filter, noise_sample);

        if (filtered) {
            false_positives++;
        }
    }

    double empirical_p = (double)false_positives / (double)TOTAL_SAMPLES;
    printf(" -> Хибних спрацювань: %u з %u\n", false_positives, TOTAL_SAMPLES);
    printf(" -> Емпірична ймовірність P_false = %e (Теоретична: ~4.01e-07)\n", empirical_p);
    assert(empirical_p < 2.0e-6 && "Помилка: рівень хибних спрацювань перевищує межу!");
    printf(" -> Монте-Карло валідацію завершено успішно.\n");
}

int main(void) {
    srand((unsigned int)time(NULL));
    printf("=== Запуск верифікаційного комплексу модуля N-з-M ===\n");
    run_contact_bounce_test();
    run_monte_carlo_validation();
    printf("Усі системні тести успішно складено.\n");
    return 0;
}
