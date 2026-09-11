#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "gearmotor_driver.h"

/*
 * ============================================================================
 * ДЕМОНСТРАЦІЯ МОДУЛЬНОГО ДРАЙВЕРА МОТОР-РЕДУКТОРА В СУПЕРЦИКЛІ
 * ============================================================================
 *
 * У цій програмі демонструється повний життєвий цикл керування приводом 6 В:
 * 1. Безпечна ініціалізація з dead-time та обмеженням темпу наростання (dI/dt).
 * 2. Плавний пуск (soft-start) без стрибка пускового струму та ударів у шестернях.
 * 3. Робота на заданій крейсерській швидкості.
 * 4. Запит реверсу: автоматичне плавне уповільнення до 0 -> витримка мертвої
 *    зони (deadband) для зупинки вала та гасіння проти-ЕРС -> плавний розгін назад.
 * 5. Активне динамічне гальмування (low-side clamp) для негайної фіксації ротора.
 * 6. Перехід у режим вільного вибігу (coasting).
 */

#define SYSTEM_TICK_MS       10U   /**< Крок системного квантування часу (10 мс) */
#define TOTAL_DEMO_TICKS     185U  /**< Загальна кількість кроків симуляції суперциклу */

/*
 * Портативна функція затримки для запобігання 100% завантаженню процесора (busy-waiting)
 * під час емуляції роботи мікроконтролерного суперциклу.
 */
#if defined(_WIN32)
#include <windows.h>
static void platform_delay_ms(uint32_t ms)
{
    Sleep(ms);
}
#elif defined(__unix__) || defined(__APPLE__)
#include <unistd.h>
static void platform_delay_ms(uint32_t ms)
{
    usleep((useconds_t)ms * 1000U);
}
#else
static void platform_delay_ms(uint32_t ms)
{
    (void)ms; /* На «голому залізі» очікування ведеться за апаратним прапорцем SysTick */
}
#endif

/**
 * @brief Виведення телеметрії приводу в консоль
 */
static void print_status(uint32_t tick_ms, const gearmotor_t *motor, const char *event_desc)
{
    const char *state_str = "НЕВІДОМО";
    switch (motor->state) {
    case MOTOR_STATE_STOP:    state_str = "STOP   "; break;
    case MOTOR_STATE_FORWARD: state_str = "FORWARD"; break;
    case MOTOR_STATE_REVERSE: state_str = "REVERSE"; break;
    case MOTOR_STATE_BRAKE:   state_str = "BRAKE  "; break;
    }

    const char *dir_str = (motor->target_dir == MOTOR_DIR_FORWARD) ? "FWD" : "REV";
    float duty_pct = ((float)motor->current_duty / (float)motor->pwm_period) * 100.0f;

    printf("  [%04u мс] | %-7s | %-3s | %4u/%4u (%5.1f%%) | %s\n",
           (unsigned int)tick_ms,
           state_str,
           dir_str,
           motor->current_duty,
           motor->pwm_period,
           (double)duty_pct,
           event_desc);
}

int main(void)
{
    printf("===============================================================================\n");
    printf("  МОДУЛЬНИЙ ДРАЙВЕР МОТОР-РЕДУКТОРА 6 В: SOFT-START, DEAD-TIME, БЕЗПЕЧНИЙ РЕВЕРС\n");
    printf("===============================================================================\n");
    printf("  [Час]     | Стан    | Напр| Шпаруватість ШІМ | Подія / Стан перехідного процесу\n");
    printf("-------------------------------------------------------------------------------\n");

    /*
     * 1. Безпечні конфігураційні параметри за замовчуванням:
     *    - pwm_period = 1000: частота ШІМ 20 кГц (вище порогу чутності людини при 20 МГц таймері)
     *    - dead_time_counts = 25: захисний час ~1.25 мкс проти наскрізного струму напівмостів
     *    - ramp_step = 25: крок зміни шпаруватості за 10 мс (повний розгін 0..100% за 400 мс)
     *    - deadband_ticks = 15: пауза 150 мс у нульовому стані для гасіння проти-ЕРС при реверсі
     */
    gearmotor_config_t config = {
        .pwm_period = 1000,
        .dead_time_counts = 25,
        .ramp_step = 25,
        .deadband_ticks = 15
    };

    gearmotor_t motor;
    if (!gearmotor_init(&motor, &config)) {
        printf("Помилка: не вдалося ініціалізувати драйвер мотора!\n");
        return 1;
    }

    /* Симуляція системного таймера (SysTick) та кроків суперциклу */
    uint32_t current_time_ms = 0;
    bool event_fwd_started = false;
    bool event_fwd_reached = false;
    bool event_rev_commanded = false;
    bool event_rev_reached = false;
    bool event_brake_commanded = false;
    bool event_stop_commanded = false;

    for (uint32_t tick = 0; tick < TOTAL_DEMO_TICKS; ++tick) {
        current_time_ms = tick * SYSTEM_TICK_MS;

        /*
         * Сценарій керування приводом за розкладом у суперциклі:
         */

        /* Крок 1: Запуск прямого обертання на 75% швидкості (750 відліків) */
        if (tick == 0 && !event_fwd_started) {
            event_fwd_started = true;
            gearmotor_set_direction(&motor, MOTOR_DIR_FORWARD);
            gearmotor_set_speed(&motor, 750);
            print_status(current_time_ms, &motor, "Команда: пуск ВПЕРЕД, ціль 750 (75%)");
        }

        /* Фіксація моменту виходу на цільову швидкість уперед */
        if (!event_fwd_reached && gearmotor_is_ramp_complete(&motor) && tick > 10 && tick < 55) {
            event_fwd_reached = true;
            print_status(current_time_ms, &motor, ">> Цільову швидкість ВПЕРЕД успішно досягнуто!");
        }

        /* Крок 2: На 60-му тіку (600 мс) — команда реверсу на швидкість 600 (60%) */
        if (tick == 60 && !event_rev_commanded) {
            event_rev_commanded = true;
            gearmotor_set_direction(&motor, MOTOR_DIR_REVERSE);
            gearmotor_set_speed(&motor, 600);
            print_status(current_time_ms, &motor, "Команда: РЕВЕРС НАЗАД, ціль 600 (60%)");
        }

        /* Фіксація моменту виходу на цільову реверсивну швидкість */
        if (event_rev_commanded && !event_rev_reached && gearmotor_is_ramp_complete(&motor) && tick > 115) {
            event_rev_reached = true;
            print_status(current_time_ms, &motor, ">> Цільову швидкість РЕВЕРСУ успішно досягнуто!");
        }

        /* Крок 3: На 145-му тіку (1450 мс) — команда активного динамічного гальмування */
        if (tick == 145 && !event_brake_commanded) {
            event_brake_commanded = true;
            gearmotor_brake(&motor);
            print_status(current_time_ms, &motor, "Команда: АКТИВНЕ ГАЛЬМУВАННЯ (low-side clamp)");
        }

        /* Крок 4: На 170-му тіку (1700 мс) — перехід у вільний вибіг (coasting) */
        if (tick == 170 && !event_stop_commanded) {
            event_stop_commanded = true;
            gearmotor_stop(&motor);
            print_status(current_time_ms, &motor, "Команда: ВІЛЬНИЙ ВИБІГ (STOP/Hi-Z)");
        }

        /*
         * Періодичне неблокувальне оновлення кінцевого автомата приводу.
         * Розраховує наступний крок наростання/спаду ШІМ та керує станом ключів.
         */
        gearmotor_update(&motor);

        /* Виведення проміжних статусів кожні 150 мс (15 тіків) для наочності графіку */
        if ((tick % 15 == 0) && (tick != 0) && (tick != 60) && (tick != 145) && (tick != 170)) {
            const char *phase_desc = "Робочий режим";
            if (motor.state == MOTOR_STATE_STOP && motor.deadband_counter > 0) {
                phase_desc = "Мертва зона реверсу (гасіння ЕРС і зупинка вала)";
            } else if (!gearmotor_is_ramp_complete(&motor)) {
                phase_desc = "Перехідний процес (софт-старт / софт-стоп)";
            } else if (motor.state == MOTOR_STATE_BRAKE) {
                phase_desc = "Активне утримання гальмом";
            }
            print_status(current_time_ms, &motor, phase_desc);
        }

        /*
         * Неблокувальна пауза симуляції (1 мс реального часу замість 100% busy-loop),
         * що дозволяє виконати симуляцію плавно та без завантаження ядер ОС.
         */
        platform_delay_ms(1);
    }

    printf("-------------------------------------------------------------------------------\n");
    printf("Демонстрацію успішно завершено. Усі перехідні процеси виконано безпечно.\n");

    return 0;
}
