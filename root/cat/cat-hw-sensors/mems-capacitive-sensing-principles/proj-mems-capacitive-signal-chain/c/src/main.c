/**
 * @file main.c
 * @brief Приклад використання C-драйвера для зчитування MEMS ємнісного давача.
 *
 * Програма ініціалізує конфігурацію дифконтуру, виконує автокалібрування
 * нуля ЦАП у стані спокою та моделює процес циклічного вимірювання
 * механічних зміщень сенсора з цифровою фільтрацією шумів.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#include "mems_capacitive.h"
#include "mems_mcu_hal.h"

int main(void)
{
    printf("===============================================================\n");
    printf("  Принципи ємнісного вимірювання в MEMS-структурах (C Driver)  \n");
    printf("===============================================================\n\n");

    /* 1. Конфігурація параметрів дифконтуру та збудження MEMS */
    mems_config_t config = {
        .excitation_freq_hz = 100000U,     /* 100 кГц частота збуджувального меандру */
        .num_samples_avg = 16U,            /* 16 вибірок на один цикл демодулювання */
        .calib_max_iterations = 12U,       /* 12 кроків бінарного пошуку для 12-біт ЦАП */
        .alpha_filter = 0.25f,             /* Коефіцієнт EMA фільтра завад */
        .sensitivity_lsb_per_ff = 15.0f,   /* Чутливість: 15.0 LSB АЦП на 1.0 fF */
        .vref_mv = 3300.0f                 /* Опорна напруга 3.3 В (3300 мВ) */
    };

    mems_dev_t dev;

    printf("[ІНІЦІАЛІЗАЦІЯ] Налаштування ШІМ-таймера (100 кГц) та периферії МК...\n");
    mems_status_t status = mems_init(&dev, &config);
    if (status != MEMS_OK) {
        printf("[ПОМИЛКА] Не вдалося ініціалізувати C-драйвер MEMS! Код: %d\n", status);
        return 1;
    }
    printf("[OK] Драйвер успішно ініціалізовано. Початковий зсув ЦАП: %u LSB\n\n", dev.dac_zero_offset_raw);

    /* 2. Виконання процедури автокалібрування зсуву нуля у статиці */
    printf("[КАЛІБРУВАННЯ] Старт пошуку зсуву нуля ЦАП для компенсації асиметрії C1/C2...\n");
    status = mems_calibrate_zero(&dev);
    if (status != MEMS_OK || dev.calib_state != MEMS_CALIB_SUCCESS) {
        printf("[ПОМИЛКА] Автокалібрування нульового зсуву завершилось неуспішно!\n");
        return 1;
    }
    printf("[OK] Автокалібрування успішно завершено!\n");
    printf("     - Зафіксований код ЦАП зсуву нуля: %u LSB\n", dev.dac_zero_offset_raw);

    int32_t residual_diff = 0;
    mems_read_differential_raw(&dev, &residual_diff);
    printf("     - Залишковий диференціальний сигнал у статиці: %d LSB\n\n", residual_diff);

    /* 3. Циклічне вимірювання динамічного зміщення ємності MEMS маси */
    printf("[ВИМІРЮВАННЯ] Моделювання механічного зміщення MEMS-маси (синусоїдальні завади та рух):\n");
    printf("-----------------------------------------------------------------------------------\n");
    printf("| Крок | Симульоване dC | Сирий вимір dC | Відфільтроване dC | Напруга dV (мВ) |\n");
    printf("-----------------------------------------------------------------------------------\n");

    /* Моделюємо 15 ітерацій вимірювального циклу */
    for (int step = 1; step <= 15; step++) {
        /*
         * Генеруємо механічне зміщення маси: гармонічне прискорення
         * dC_phys = A * sin(2 * pi * step / T) з амплітудою 35.0 fF
         */
        float sim_dC = 35.0f * sinf(2.0f * 3.14159265f * (float)step / 10.0f);

        /* Оновлюємо фізичний стан симулятора MEMS */
        mems_hal_sim_set_displacement(sim_dC);

        /* Повний цикл зчитування, демодулювання та EMA фільтрації */
        status = mems_process_sample(&dev);
        if (status != MEMS_OK) {
            printf("| %02d   | ПОМИЛКА ОЦИФРУВАННЯ (%d)                                          |\n", step, status);
            continue;
        }

        float instant_dC = 0.0f;
        float filtered_dC = 0.0f;
        mems_get_capacitance_diff(&dev, &instant_dC);
        mems_get_filtered_capacitance(&dev, &filtered_dC);

        printf("| %02d   |   %+7.2f fF   |   %+7.2f fF  |    %+7.2f fF     |   %+8.2f мВ  |\n",
               step, sim_dC, instant_dC, filtered_dC, dev.diff_voltage_mv);
    }
    printf("-----------------------------------------------------------------------------------\n\n");

    /* 4. Перевірка обробки некоректних аргументів */
    printf("[ТЕСТ ПОМИЛОК] Перевірка стійкості драйвера до некоректних аргументів:\n");
    mems_status_t err_test = mems_process_sample(NULL);
    printf(" - Виклик mems_process_sample(NULL): повернено %d (очікувалось %d)\n",
           err_test, MEMS_ERR_INVALID_ARG);

    printf("\nДемонстрацію роботи C-драйвера MEMS-структури успішно завершено.\n");
    return 0;
}
