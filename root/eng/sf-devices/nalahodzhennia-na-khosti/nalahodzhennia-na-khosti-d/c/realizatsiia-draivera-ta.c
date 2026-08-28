#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HISTORY_DEPTH 4

typedef struct {
    int32_t history[HISTORY_DEPTH];
    uint8_t count;
    bool is_calibrated; /* Якщо не ініціалізувати — сміття на стеку */
} telemetry_filter_t;

/* Обчислення тиску в Паскалях за формулою компенсації */
int32_t calculate_compensated_pressure(int32_t raw_adc, int32_t calib_p1, int32_t calib_p2) {
    /* БАГ 1 (UBSan): Знакове переповнення при великих значеннях raw_adc та calib_p1 */
    int32_t intermediate = raw_adc * calib_p1; 
    int32_t pressure_pa = (intermediate / 100) + calib_p2;
    return pressure_pa;
}

/* Додавання заміру до фільтра ковзного середнього */
void telemetry_filter_add(telemetry_filter_t *filter, int32_t sample) {
    /* БАГ 2 (ASan): Відсутність захисту від перевищення індексу масиву */
    filter->history[filter->count] = sample; 
    filter->count++;
}

int32_t telemetry_filter_get_average(const telemetry_filter_t *filter) {
    /* БАГ 3 (Valgrind): Перевірка неініціалізованого поля is_calibrated */
    if (!filter->is_calibrated) {
        return 0;
    }

    if (filter->count == 0) {
        return 0;
    }

    int64_t sum = 0;
    uint8_t limit = filter->count > HISTORY_DEPTH ? HISTORY_DEPTH : filter->count;
    for (uint8_t i = 0; i < limit; ++i) {
        sum += filter->history[i];
    }
    return (int32_t)(sum / limit);
}

int main(void) {
    printf("=== Запуск демонстраційного драйвера ===\n");

    /* Тест 1: Перевірка формули тиску (викликає Signed Integer Overflow) */
    int32_t p = calculate_compensated_pressure(60000, 50000, 101325);
    printf("Обчислений тиск: %d Па\n", p);

    /* Тест 2: Заповнення фільтра (викликає Stack Buffer Overflow та Uninitialized Read) */
    telemetry_filter_t filter;
    /* Навмисно не викликаємо memset, щоб поля count та is_calibrated містили сміття */
    filter.count = 0; 
    /* filter.is_calibrated не ініціалізовано! */

    for (int i = 0; i < 6; ++i) { /* 6 ітерацій при розмірі масиву 4! */
        telemetry_filter_add(&filter, 1000 + i * 10);
    }

    int32_t avg = telemetry_filter_get_average(&filter);
    printf("Середній тиск: %d\n", avg);

    return 0;
}
