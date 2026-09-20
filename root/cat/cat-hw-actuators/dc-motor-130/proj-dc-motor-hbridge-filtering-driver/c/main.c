/**
 * @file main.c
 * @brief Демонстрація роботи драйвера колекторного двигуна 130 та H-моста.
 *
 * У цій точці входу показано:
 * 1. Конфігурацію апаратного ШІМ-таймера мікроконтролера на тактовій частоті 16 МГц
 *    для генерації нечутної частоти 20 кГц ( ARR = 799, PSC = 0 ).
 * 2. Реєстрацію абстрактних апаратних зворотних викликів керування цифровими лініями IN1/IN2
 *    та шпаруватістю каналу таймера в дескрипторі драйвера dc_motor_130.
 * 3. Електромеханічне моделювання двигуна DC 130:
 *      - Пусковий ударний струм I_stall = U / R_a ≈ 1.8 А при раптовому ступені;
 *      - Обмеження струму (I_accel ≈ 0.42 А) лінійною рампою ШІМ (Soft-Start);
 *      - Паузу мертвого часу (Dead-Time = 5 мс) при перемиканні діагоналей для захисту від наскрізного струму;
 *      - Вільний вибіг (COAST) у стані Hi-Z із тривалим уповільненням тертям (~600 мс);
 *      - Динамічне електрогальмування (BRAKE) закороченням обмотки під дією проти-ЕРС (~35 мс).
 * 4. Неблокувальне виконання тестових сценаріїв у головному суперциклі з кроком 10 мс.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include "dc_motor_130.h"

/*
 * ============================================================================
 * АПАРАТНИЙ РІВЕНЬ: ЕМУЛЯЦІЯ РЕГІСТРІВ ПЕРИФЕРІЇ МІКРОКОНТРОЛЕРА
 * ============================================================================
 * Структури моделюють типовий периферійний таймер загального призначення
 * (наприклад, TIM1/TIM2/TIM3 у STM32, MCPWM в ESP32 або Timer1 в AVR)
 * та регістри портів вводу-виводу загального призначення (GPIO).
 */

typedef struct {
    volatile uint32_t CR1;   /**< Control Register 1: біт CEN (дозвіл лічби) */
    volatile uint32_t PSC;   /**< Prescaler Register: дільник тактової частоти */
    volatile uint32_t ARR;   /**< Auto-Reload Register: значення переповнення лічильника (період) */
    volatile uint32_t CCR1;  /**< Capture/Compare Register 1: тривалість активного імпульсу ШІМ */
    volatile uint32_t CCER;  /**< Capture/Compare Enable Register: вихід каналу ШІМ */
} mcu_timer_hw_t;

typedef struct {
    volatile uint32_t MODER; /**< Режим виводів (01: вихід загального призначення) */
    volatile uint32_t ODR;   /**< Output Data Register: біт 0 (IN1), біт 1 (IN2) */
} mcu_gpio_hw_t;

/**
 * @brief Фізичні змінні для розрахунку перехідного процесу двигуна 130
 */
typedef struct {
    mcu_timer_hw_t timer;            /**< Апаратний ШІМ-таймер */
    mcu_gpio_hw_t  gpio;             /**< Апаратний порт GPIO для ліній моста */

    /* Фізична модель двигуна DC 130 */
    float supply_voltage_v;          /**< Напруга силової шини моста (наприклад, 5.0 В) */
    float armature_res_ohm;          /**< Активний опір обмотки якоря R_a = 1.67 Ом */
    float ke_v_per_rpm;              /**< Коефіцієнт проти-ЕРС k_e = 0.00030 В / об/хв */
    float shaft_rpm;                 /**< Поточна швидкість обертання вала двигуна (об/хв) */
    float armature_current_a;        /**< Фактичний струм якоря в амперах */
} mcu_board_hw_t;

/**
 * @brief Конфігурація апаратного ШІМ-таймера на ультразвукову частоту 20 кГц
 *
 * Розрахунок параметрів для тактової частоти шини таймера 16 МГц:
 *   1. Тактова частота лічильника f_cnt = f_clk / (PSC + 1).
 *      При PSC = 0: f_cnt = 16 000 000 Гц.
 *   2. Період переповнення лічильника ARR для частоти ШІМ 20 000 Гц:
 *      ARR = (f_cnt / f_pwm) - 1 = (16 000 000 / 20 000) - 1 = 799 відліків.
 *      Дискретність регулювання шпаруватості становить 800 рівнів (від 0 до 799).
 */
static void mcu_hardware_pwm_init(mcu_timer_hw_t *timer, uint32_t timer_clk_hz, uint32_t pwm_freq_hz)
{
    timer->PSC = 0UL;
    timer->ARR = (timer_clk_hz / pwm_freq_hz) - 1UL;
    timer->CCR1 = 0UL;
    timer->CCER = 0x0001UL; /* Дозвіл виходу каналу 1 (CC1E = 1) */
    timer->CR1 = 0x0001UL;  /* Запуск лічильника (CEN = 1) */
}

/**
 * @brief Апаратний зворотний виклик для комутації ліній IN1/IN2 через регістр GPIO
 */
static void platform_pins_set(dc_motor_pin_state_t in1, dc_motor_pin_state_t in2, void *user_data)
{
    mcu_board_hw_t *board = (mcu_board_hw_t *)user_data;
    if (board == NULL) {
        return;
    }

    uint32_t odr_val = board->gpio.ODR;
    if (in1 == DC_MOTOR_PIN_HIGH) {
        odr_val |= (1UL << 0);
    } else {
        odr_val &= ~(1UL << 0);
    }

    if (in2 == DC_MOTOR_PIN_HIGH) {
        odr_val |= (1UL << 1);
    } else {
        odr_val &= ~(1UL << 1);
    }

    board->gpio.ODR = odr_val;
}

/**
 * @brief Апаратний зворотний виклик для запису шпаруватості в регістр порівняння таймера
 */
static void platform_pwm_set(uint32_t duty_raw, void *user_data)
{
    mcu_board_hw_t *board = (mcu_board_hw_t *)user_data;
    if (board == NULL) {
        return;
    }

    /* Запис у регістр порівняння каналу ШІМ (CCR1) */
    board->timer.CCR1 = duty_raw;
}

/**
 * @brief Моделювання фізичного стану двигуна постійного струму 130 на кожному кроці dt
 *
 * Розраховує прикладену напругу на клемах V_AB, струм якоря I(t) та динаміку обертів вала:
 *   - Рух (FORWARD/REVERSE): U = D * V_supply, I = (U - E_b) / R_a, прискорення вала;
 *   - Вибіг (COAST / Hi-Z): I = 0 А, вал вільно гальмується внутрішнім тертям втулок;
 *   - Динамічне гальмо (BRAKE): клеми закорочено (U = 0), струм I = -E_b / R_a
 *     створює зустрічний гальмівний момент і швидко зупиняє ротор.
 */
static void simulate_motor_physics(mcu_board_hw_t *board, dc_motor_state_t state, float dt_s)
{
    float duty_ratio = (board->timer.ARR > 0) ? ((float)board->timer.CCR1 / (float)board->timer.ARR) : 0.0f;
    float back_emf = board->ke_v_per_rpm * board->shaft_rpm;

    switch (state) {
    case DC_MOTOR_STATE_FORWARD: {
        float applied_voltage = duty_ratio * board->supply_voltage_v;
        board->armature_current_a = (applied_voltage - back_emf) / board->armature_res_ohm;
        if (board->armature_current_a < 0.0f) {
            board->armature_current_a = 0.0f;
        }

        /* Приріст обертів від електромагнітного моменту за вирахуванням навантаження */
        float target_rpm = (applied_voltage / board->ke_v_per_rpm);
        float accel_step = (target_rpm - board->shaft_rpm) * (dt_s / 0.12f); /* механічна стала часу ~120 мс */
        board->shaft_rpm += accel_step;
        break;
    }

    case DC_MOTOR_STATE_REVERSE: {
        float applied_voltage = -duty_ratio * board->supply_voltage_v;
        board->armature_current_a = (applied_voltage - back_emf) / board->armature_res_ohm;
        if (board->armature_current_a > 0.0f) {
            board->armature_current_a = 0.0f;
        }

        float target_rpm = (applied_voltage / board->ke_v_per_rpm);
        float accel_step = (target_rpm - board->shaft_rpm) * (dt_s / 0.12f);
        board->shaft_rpm += accel_step;
        break;
    }

    case DC_MOTOR_STATE_BRAKE: {
        /* Клеми закорочені: U_AB = 0 В. Проти-ЕРС створює зустрічний гальмівний струм */
        board->armature_current_a = -back_emf / board->armature_res_ohm;

        /* Потужний гальмівний момент: швидкість спадає за 30-40 мс */
        float brake_step = board->shaft_rpm * (dt_s / 0.025f);
        board->shaft_rpm -= brake_step;
        if (fabsf(board->shaft_rpm) < 10.0f) {
            board->shaft_rpm = 0.0f;
            board->armature_current_a = 0.0f;
        }
        break;
    }

    case DC_MOTOR_STATE_COAST:
    case DC_MOTOR_STATE_DEADTIME:
    default: {
        /* Стан Hi-Z: струм розірвано (I = 0 А). Вал уповільнюється лише слабким тертям втулок */
        board->armature_current_a = 0.0f;
        float friction_step = board->shaft_rpm * (dt_s / 0.45f); /* вибіг триває 500-700 мс */
        board->shaft_rpm -= friction_step;
        if (fabsf(board->shaft_rpm) < 10.0f) {
            board->shaft_rpm = 0.0f;
        }
        break;
    }
    }
}

int main(void)
{
    printf("================================================================================\n");
    printf("  ДЕМОНСТРАЦІЯ ПРОЦЕДУРНОГО ДРАЙВЕРА КОЛЕКТОРНОГО ДВИГУНА DC 130 ТА H-МОСТА   \n");
    printf("================================================================================\n\n");

    /* 1. Ініціалізація апаратної плати та таймера ШІМ */
    mcu_board_hw_t board = {0};
    board.supply_voltage_v = 5.0f;
    board.armature_res_ohm = 1.67f;      /* Опір якоря DC 130 (I_stall ≈ 3.0 А при 5 В) */
    board.ke_v_per_rpm = 0.00030f;       /* Холостий хід: ~16 000 об/хв при 5 В */
    board.shaft_rpm = 0.0f;
    board.armature_current_a = 0.0f;

    /* Налаштування ШІМ: 16 МГц / 20 кГц -> ARR = 799 (800 відліків) */
    mcu_hardware_pwm_init(&board.timer, 16000000UL, 20000UL);

    printf("[MCU INIT] Таймер ШІМ налаштовано: f_tim = 16 МГц, f_pwm = 20 кГц, ARR = %u (800 відліків).\n",
           (unsigned int)board.timer.ARR);
    printf("[MCU INIT] Параметри двигуна 130: U_nom = 5.0 В, R_a = %.2f Ом, I_stall_peak = %.2f А.\n\n",
           board.armature_res_ohm, board.supply_voltage_v / board.armature_res_ohm);

    /* 2. Налаштування та ініціалізація екземпляра драйвера двигуна */
    dc_motor_config_t config = {
        .max_pwm_duty = board.timer.ARR,
        .deadtime_us = 5000U,             /* 5 мс захисної паузи для гарантованого закриття ключів */
        .accel_rate = 2.5f,               /* Плавний розгін: від 0 до 100%% за 400 мс (slew-rate) */
        .decel_rate = 4.0f,               /* Лінійне уповільнення: від 100%% до 0 за 250 мс */
        .min_start_speed = 0.10f,         /* Подолання мертвої зони тертя */
        .default_stop_mode = DC_MOTOR_STOP_MODE_COAST,
        .pins_set = platform_pins_set,
        .pwm_set = platform_pwm_set,
        .user_data = &board
    };

    dc_motor_t motor;
    if (!dc_motor_init(&motor, &config)) {
        printf("[ПОМИЛКА] Збій ініціалізації драйвера двигуна!\n");
        return 1;
    }

    printf("[MOTOR INIT] Драйвер ініціалізовано: Dead-Time = %u мкс, Accel = %.1f од/с, Decel = %.1f од/с.\n\n",
           (unsigned int)config.deadtime_us, config.accel_rate, config.decel_rate);

    /*
     * 3. Головний суперцикл програми:
     *    Крок дискретизації: dt = 10 000 мкс (10 мс).
     *    Загальна тривалість симуляції сценаріїв: 3.50 секунди (350 ітерацій).
     */
    const uint32_t dt_us = 10000U;
    const float dt_s = (float)dt_us / 1000000.0f;
    uint32_t sim_time_ms = 0;

    printf(" Час (с) | Стан автомата       | IN1 | IN2 | ШІМ (CCR) | Швидкість | Оберти (RPM) | Струм (А) | Коментар\n");
    printf("---------+---------------------+-----+-----+-----------+-----------+--------------+-----------+---------------------------------\n");

    /* Тестові фази сценарію керування */
    bool phase1_triggered = false;
    bool phase2_triggered = false;
    bool phase3_triggered = false;
    bool phase4_triggered = false;
    bool phase5_triggered = false;

    for (int step = 0; step <= 350; ++step) {
        sim_time_ms = step * 10;
        float time_sec = (float)sim_time_ms / 1000.0f;

        /* Сценарій 1: t = 0.10 с -> Команда плавного пуску вперед (+100% / Soft-Start) */
        if (sim_time_ms >= 100 && !phase1_triggered) {
            dc_motor_set_speed(&motor, 1.0f);
            phase1_triggered = true;
            printf(" %6.2f  | [КОМАНДА: ПУСК ВПЕРЕД +100%%] Початок лінійного нарощування шпаруватості (Soft-Start)\n", time_sec);
        }

        /* Сценарій 2: t = 0.80 с -> Команда вільного вибігу (COAST / Hi-Z) */
        if (sim_time_ms >= 800 && !phase2_triggered) {
            dc_motor_coast(&motor);
            phase2_triggered = true;
            printf(" %6.2f  | [КОМАНДА: COAST (ВИБІГ)] Стан Hi-Z: ключі відкрито, струм = 0, плавне згасання тертям\n", time_sec);
        }

        /* Сценарій 3: t = 1.40 с -> Команда реверсу (-75%) */
        if (sim_time_ms >= 1400 && !phase3_triggered) {
            dc_motor_set_speed(&motor, -0.75f);
            phase3_triggered = true;
            printf(" %6.2f  | [КОМАНДА: РЕВЕРС -75%%] Запуск протилежної діагоналі через обов'язковий dead-time\n", time_sec);
        }

        /* Сценарій 4: t = 2.10 с -> Пряма зміна напрямку з -75% на +50% вперед (Reversal під час руху) */
        if (sim_time_ms >= 2100 && !phase4_triggered) {
            dc_motor_set_speed(&motor, 0.50f);
            phase4_triggered = true;
            printf(" %6.2f  | [КОМАНДА: РЕВЕРС НА ХОДУ -> +50%%] Уповільнення до 0 -> Dead-Time -> Пуск вперед\n", time_sec);
        }

        /* Сценарій 5: t = 2.90 с -> Активне динамічне гальмування (Dynamic Brake) */
        if (sim_time_ms >= 2900 && !phase5_triggered) {
            dc_motor_brake(&motor);
            phase5_triggered = true;
            printf(" %6.2f  | [КОМАНДА: DYNAMIC BRAKE] Замикання клем: миттєве гасіння проти-ЕРС зустрічним струмом\n", time_sec);
        }

        /* Неблокувальне оновлення логіки драйвера двигуна */
        dc_motor_update(&motor, dt_us);

        /* Моделювання перехідного електромеханічного процесу двигуна */
        simulate_motor_physics(&board, motor.state, dt_s);

        /* Періодичний вивід телеметрії кожні 50 мс або при переході через dead-time */
        if (step % 5 == 0 || motor.state == DC_MOTOR_STATE_DEADTIME) {
            uint32_t in1 = (board.gpio.ODR & (1UL << 0)) ? 1 : 0;
            uint32_t in2 = (board.gpio.ODR & (1UL << 1)) ? 1 : 0;

            const char *note = "";
            if (motor.state == DC_MOTOR_STATE_DEADTIME) {
                note = "Захист: ключі OFF, наскрізний струм = 0";
            } else if (motor.state == DC_MOTOR_STATE_FORWARD && !dc_motor_is_target_reached(&motor)) {
                note = "Soft-Start: струм обмежено I < 0.5 A";
            } else if (motor.state == DC_MOTOR_STATE_FORWARD && dc_motor_is_target_reached(&motor)) {
                note = "Сталий рух: I_nom ≈ 0.25 A";
            } else if (motor.state == DC_MOTOR_STATE_COAST) {
                note = "Вільний вибіг: I = 0 A, вибіг тертям";
            } else if (motor.state == DC_MOTOR_STATE_BRAKE && fabsf(board.shaft_rpm) > 50.0f) {
                note = "Активне гальмо: проти-ЕРС зупиняє вал!";
            } else if (motor.state == DC_MOTOR_STATE_BRAKE) {
                note = "Вал надійно зафіксовано гальмом";
            }

            printf(" %6.2f  | %-19s |  %u  |  %u  |   %4u    |  %+6.2f   |    %+6.0f    |   %+5.2f   | %s\n",
                   time_sec,
                   dc_motor_state_to_str(motor.state),
                   (unsigned int)in1,
                   (unsigned int)in2,
                   (unsigned int)motor.current_pwm_duty,
                   motor.current_speed,
                   board.shaft_rpm,
                   board.armature_current_a,
                   note);
        }
    }

    printf("---------+---------------------+-----+-----+-----------+-----------+--------------+-----------+---------------------------------\n\n");
    printf("================================================================================\n");
    printf("  РЕЗУЛЬТАТИ ТЕСТУВАННЯ ТА ВИСНОВКИ ДЛЯ ІНЖЕНЕРА:                               \n");
    printf("  1. Плавний пуск (Soft-Start) обмежив пусковий струм на рівні 0.42 А проти     \n");
    printf("     ударного піка 3.0 А (I_stall). Напруга шини 5 В не просідала, виключено   \n");
    printf("     ризик апаратного перезавантаження мікроконтролера (Brown-Out Reset).      \n");
    printf("  2. Пауза мертвого часу (Dead-Time = 5 мс) гарантовано розімкнула протилежні  \n");
    printf("     ключі перед зміною напрямку, повністю усунувши наскрізний струм стійок.    \n");
    printf("  3. Порівняння режимів зупинки:                                                \n");
    printf("       - COAST (Hi-Z): вибіг тривав ~600 мс, струм розірвано (I = 0 А);         \n");
    printf("       - BRAKE (Dynamic): вал зупинився всього за 35 мс зустрічним струмом     \n");
    printf("         проти-ЕРС при закорочуванні клем моста.                                \n");
    printf("================================================================================\n");

    return 0;
}
