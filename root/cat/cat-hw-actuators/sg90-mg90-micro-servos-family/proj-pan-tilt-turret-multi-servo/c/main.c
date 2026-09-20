/**
 * @file main.c
 * @brief Демонстрація роботи процедурного драйвера двоосьового модуля Pan-Tilt (C99).
 *
 * Програма ілюструє:
 * 1. Низькорівневу конфігурацію двох незалежних каналів 50-Гц апаратного ШІМ-таймера (16 МГц шина, 1 мкс такт);
 * 2. Апаратні відмінності приводів Tower Pro в одній системі:
 *    - Вісь Pan (панорамування): MG90S із металевим редуктором (вищий момент, більша кутова швидкість);
 *    - Вісь Tilt (нахил камери): SG90 із нейлоновим редуктором (легкий, делікатне прискорення проти зрізання зубців);
 * 3. Індивідуальне програмне калібрування зсуву нейтралі (trim offset) для усунення перекосу качалок;
 * 4. Захисні софт-ліміти: блокування спроб виходу за межі шарніра й механічних упорів корпусу;
 * 5. Неблокувальне скоординоване переміщення осей у суперциклі без викликів затримок delay().
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include "servo_driver.h"

/*
 * ============================================================================
 * АПАРАТНИЙ РІВЕНЬ: ЕМУЛЯЦІЯ ДВОКАНАЛЬНОГО ШІМ-ТАЙМЕРА МІКРОКОНТРОЛЕРА
 * ============================================================================
 * Модель відповідає апаратному таймеру загального призначення (TIM2/TIM3 у STM32,
 * MCPWM в ESP32 або 16-бітному Timer1 в AVR ATmega328P).
 */
typedef struct {
    volatile uint32_t CR1;   /**< Control Register 1: біт 0 (CEN) — запуск лічби */
    volatile uint32_t PSC;   /**< Prescaler: подільник тактової частоти */
    volatile uint32_t ARR;   /**< Auto-Reload: період 20 мс (20 000 відліків при 1 МГц) */
    volatile uint32_t CCR1;  /**< Capture/Compare 1: тривалість імпульсу Pan (MG90S), мкс */
    volatile uint32_t CCR2;  /**< Capture/Compare 2: тривалість імпульсу Tilt (SG90), мкс */
    volatile uint32_t CCER;  /**< Capture/Compare Enable: дозвіл виходів каналів */
} mcu_timer_hw_t;

/**
 * @brief Ініціалізація апаратного ШІМ-таймера на частоту 50 Гц для двох каналів
 *
 * @param timer Вказівник на структуру регістрів таймера.
 * @param bus_clock_hz Тактова частота шини периферії мікроконтролера (наприклад, 16 МГц).
 * @param pwm_freq_hz Бажана частота ШІМ для сервоприводів (50 Гц).
 */
static void mcu_timer_pwm_dual_init(mcu_timer_hw_t *timer, uint32_t bus_clock_hz, uint32_t pwm_freq_hz)
{
    /*
     * 1. Розрахунок переддільника PSC для тактування лічильника з частотою 1 МГц (1 такт = 1 мкс):
     *      f_cnt = bus_clock_hz / (PSC + 1) = 1 000 000 Гц
     *      PSC = (16 000 000 / 1 000 000) - 1 = 15.
     */
    uint32_t timer_cnt_freq = 1000000UL;
    timer->PSC = (bus_clock_hz / timer_cnt_freq) - 1UL;

    /*
     * 2. Розрахунок періоду повторення імпульсів (ARR):
     *    Період T = 20 мс (50 Гц). При кроці 1 мкс це рівно 20 000 відліків:
     *      ARR = (1 000 000 / 50) - 1 = 19 999 відліків (від 0 до 19 999).
     */
    timer->ARR = (timer_cnt_freq / pwm_freq_hz) - 1UL;

    /* 3. Початкові значення шпаруватості — номінальна нейтраль 1500 мкс для обох осей */
    timer->CCR1 = SERVO_DEFAULT_NEUTRAL_US;
    timer->CCR2 = SERVO_DEFAULT_NEUTRAL_US;

    /* 4. Увімкнення виходів каналів 1 і 2 (CC1E = 1, CC2E = 1) */
    timer->CCER = 0x0011UL;

    /* 5. Запуск лічильника (CEN = 1) */
    timer->CR1 = 0x0001UL;
}

/**
 * @brief Апаратний зворотний виклик для осі Pan: запис тривалості в канал CCR1
 */
static void pan_pwm_write(uint32_t pulse_us, void *user_data)
{
    mcu_timer_hw_t *timer = (mcu_timer_hw_t *)user_data;
    if (timer != NULL) {
        timer->CCR1 = pulse_us;
    }
}

/**
 * @brief Апаратний зворотний виклик для осі Tilt: запис тривалості в канал CCR2
 */
static void tilt_pwm_write(uint32_t pulse_us, void *user_data)
{
    mcu_timer_hw_t *timer = (mcu_timer_hw_t *)user_data;
    if (timer != NULL) {
        timer->CCR2 = pulse_us;
    }
}

/*
 * ============================================================================
 * ФІЗИЧНА Й ЕЛЕКТРИЧНА МОДЕЛЬ НАВАНТАЖЕННЯ ДВООСЬОВОГО МОДУЛЯ
 * ============================================================================
 */

/**
 * @brief Розрахунок струму споживання приводу залежно від швидкості та прискорення
 *
 * Враховує фізику мікроелектродвигуна постійного струму:
 * I_total = I_quiescent + I_load(omega) + I_accel(d_omega/dt).
 */
static float estimate_servo_current_ma(const servo_t *servo, bool is_metal_gear)
{
    if (servo->state == SERVO_STATE_IDLE) {
        return is_metal_gear ? 12.0f : 8.5f; /* Струм спокою схеми керування та утримання вала */
    }

    float v_norm = fabsf(servo->current_velocity_deg_s) / servo->kinematics.max_velocity_deg_s;
    float base_dyn = is_metal_gear ? 140.0f : 90.0f;
    float cruise_add = is_metal_gear ? 160.0f : 110.0f;
    float accel_add = (servo->state == SERVO_STATE_ACCEL) ? (is_metal_gear ? 120.0f : 70.0f) : 0.0f;

    return base_dyn + v_norm * cruise_add + accel_add;
}

/**
 * @brief Друк рядка таблиці телеметрії головного суперциклу
 */
static void print_telemetry_row(uint32_t time_ms,
                                const servo_t *pan,
                                const servo_t *tilt,
                                float total_current_ma,
                                float bus_voltage_v,
                                const char *note)
{
    printf(" [%4u мс] | %5.1f° (%+5.0f°/с) | %4u мкс | %5.1f° (%+5.0f°/с) | %4u мкс | %5.1f мА | %4.2f В | %s\n",
           (unsigned int)time_ms,
           (double)pan->current_angle_deg,
           (double)pan->current_velocity_deg_s,
           pan->current_pulse_us,
           (double)tilt->current_angle_deg,
           (double)tilt->current_velocity_deg_s,
           tilt->current_pulse_us,
           (double)total_current_ma,
           (double)bus_voltage_v,
           note);
}

int main(void)
{
    printf("========================================================================================================\n");
    printf("  МОДУЛЬНИЙ ДРАЙВЕР СІМЕЙСТВА 9г МІКРОСЕРВОПРИВОДІВ TOWER PRO (SG90 / MG90S) З ШІМ 50 Гц (C99)          \n");
    printf("========================================================================================================\n\n");

    /* ------------------------------------------------------------------------
     * ЕТАП 1: НАЛАШТУВАННЯ АПАРАТНОГО ТАЙМЕРА МІКРОКОНТРОЛЕРА
     * ------------------------------------------------------------------------ */
    mcu_timer_hw_t timer_hw;
    const uint32_t SYSTEM_CLOCK_HZ = 16000000UL; /* Тактова частота шини мікроконтролера: 16 МГц */
    const uint32_t SERVO_PWM_FREQ_HZ = 50UL;     /* Частота оновлення сервоприводів: 50 Гц */

    mcu_timer_pwm_dual_init(&timer_hw, SYSTEM_CLOCK_HZ, SERVO_PWM_FREQ_HZ);

    printf("1. НАЛАШТУВАННЯ АПАРАТНОГО ТАЙМЕРА ДЛЯ 2 КАНАЛІВ ШІМ:\n");
    printf("   - Тактова частота шини:      %u Гц\n", (unsigned int)SYSTEM_CLOCK_HZ);
    printf("   - Переддільник PSC:          %u (тактування лічильника 1 МГц, дискретність 1 мкс)\n",
           (unsigned int)timer_hw.PSC);
    printf("   - Регістр автоперезавантаження ARR: %u (період 20 000 мкс = 20.0 мс, 50.0 Гц)\n",
           (unsigned int)timer_hw.ARR);
    printf("   - Канал 1 (CCR1 - Pan):      %u мкс (початкова нейтраль)\n", (unsigned int)timer_hw.CCR1);
    printf("   - Канал 2 (CCR2 - Tilt):     %u мкс (початкова нейтраль)\n\n", (unsigned int)timer_hw.CCR2);

    /* ------------------------------------------------------------------------
     * ЕТАП 2: КОНФІГУРАЦІЯ ОСЕЙ PAN (MG90S) ТА TILT (SG90)
     * ------------------------------------------------------------------------ */
    printf("2. СПЕЦИФІКАЦІЯ ТА КОНФІГУРАЦІЯ ПРИВОДІВ В ОСЯХ МЕХАНІЗМУ:\n");

    /*
     * Вісь Pan (горизонтальне панорамування):
     * Привід: Tower Pro MG90S із металевим редуктором (латунь + алюміній 6061).
     * Здатний витримувати вищі динамічні моменти інерції платформи камери (до 2.2 кг·см).
     * Встановлюємо динамічні межі: швидкість 150 °/с, прискорення 400 °/с².
     * Софт-ліміти: [10.0° .. 170.0°] (захист кабельного шлейфа від скручування та упору).
     * Зсув калібрування нейтралі: +18 мкс (компенсація технологічного люфту шліців).
     */
    servo_config_t pan_cfg = {
        .calib = {
            .min_pulse_us     = SERVO_DEFAULT_MIN_PULSE_US,
            .max_pulse_us     = SERVO_DEFAULT_MAX_PULSE_US,
            .neutral_pulse_us = SERVO_DEFAULT_NEUTRAL_US,
            .trim_offset_us   = +18
        },
        .limits = {
            .min_angle_deg    = 10.0f,
            .max_angle_deg    = 170.0f
        },
        .kinematics = {
            .max_velocity_deg_s = 150.0f,
            .max_accel_deg_s2   = 400.0f
        },
        .pwm_write = pan_pwm_write,
        .user_data = &timer_hw,
        .initial_angle_deg = 90.0f
    };

    /*
     * Вісь Tilt (вертикальний нахил оптичного сенсора):
     * Привід: Tower Pro SG90 із пластиковим (нейлоновим) редуктором.
     * Низька маса (9 г), проте зубці чутливі до ударного зрізання при різкому гальмуванні.
     * Встановлюємо делікатніший профіль: швидкість 90 °/с, прискорення 220 °/с².
     * Софт-ліміти: [15.0° .. 125.0°] (фізичні конструктивні межі нахилу кронштейна).
     * Зсув калібрування нейтралі: -24 мкс (компенсація спайки внутрішнього потенціометра).
     */
    servo_config_t tilt_cfg = {
        .calib = {
            .min_pulse_us     = SERVO_DEFAULT_MIN_PULSE_US,
            .max_pulse_us     = SERVO_DEFAULT_MAX_PULSE_US,
            .neutral_pulse_us = SERVO_DEFAULT_NEUTRAL_US,
            .trim_offset_us   = -24
        },
        .limits = {
            .min_angle_deg    = 15.0f,
            .max_angle_deg    = 125.0f
        },
        .kinematics = {
            .max_velocity_deg_s = 90.0f,
            .max_accel_deg_s2   = 220.0f
        },
        .pwm_write = tilt_pwm_write,
        .user_data = &timer_hw,
        .initial_angle_deg = 90.0f
    };

    servo_t pan_servo;
    servo_t tilt_servo;

    if (!servo_init(&pan_servo, &pan_cfg) || !servo_init(&tilt_servo, &tilt_cfg)) {
        printf("[ПОМИЛКА]: Не вдалося ініціалізувати екземпляри сервоприводів!\n");
        return 1;
    }

    printf("   [Pan  - MG90S]: Металевий редуктор | Софт-ліміти [%4.1f° .. %4.1f°] | Trim: %+d мкс | V_max: %4.0f°/с | A_max: %4.0f°/с²\n",
           (double)pan_servo.limits.min_angle_deg, (double)pan_servo.limits.max_angle_deg,
           servo_get_neutral_trim(&pan_servo),
           (double)pan_servo.kinematics.max_velocity_deg_s, (double)pan_servo.kinematics.max_accel_deg_s2);
    printf("   [Tilt - SG90 ]: Нейлоновий редуктор| Софт-ліміти [%4.1f° .. %4.1f°] | Trim: %+d мкс | V_max: %4.0f°/с | A_max: %4.0f°/с²\n",
           (double)tilt_servo.limits.min_angle_deg, (double)tilt_servo.limits.max_angle_deg,
           servo_get_neutral_trim(&tilt_servo),
           (double)tilt_servo.kinematics.max_velocity_deg_s, (double)tilt_servo.kinematics.max_accel_deg_s2);
    printf("   -> Ефективна нейтраль 90°: Pan CCR1 = %u мкс, Tilt CCR2 = %u мкс (калібрування застосовано)\n\n",
           timer_hw.CCR1, timer_hw.CCR2);

    /* ------------------------------------------------------------------------
     * ЕТАП 3: ГОЛОВНИЙ СУПЕРЦИКЛ — СКООРДИНОВАНИЙ РУХ ТА ЗАХИСТ СОФТ-ЛІМІТАМИ
     * ------------------------------------------------------------------------ */
    printf("3. ДЕМОНСТРАЦІЯ НЕБЛОКУВАЛЬНОГО СУПЕРЦИКЛУ (КРОК ДИСПЕТЧЕРА dt = 20 мс, ШІМ 50 Гц):\n");
    printf("--------------------------------------------------------------------------------------------------------\n");
    printf("   ЧАС      |    PAN (MG90S)     |  CCR1   |    TILT (SG90)     |  CCR2   |  СТРУМ   | НАПРУГА | ПОДІЯ ТА СТАН СИСТЕМИ\n");
    printf("--------------------------------------------------------------------------------------------------------\n");

    const uint32_t DT_MS = 20U; /* Період суперциклу 20 мс збігається з періодом ШІМ 50 Гц */
    uint32_t sim_time_ms = 0U;

    /*
     * План руху двоосьового модуля:
     *   0 .. 100 мс:   Старт у нейтральній точці (Pan = 90°, Tilt = 90°).
     * 100 .. 1200 мс:  Скоординована точка спостереження 1: Pan -> 40.0°, Tilt -> 30.0°.
     * 1200 .. 2400 мс: Точка спостереження 2: Pan -> 145.0°, Tilt -> 110.0° (широке сканування).
     * 2400 .. 3600 мс: ТЕСТ БЕЗПЕКИ! Спроба задати небезпечні кути поза межами:
     *                  Pan -> -25.0° (загроза удару об упор 0°),
     *                  Tilt -> 160.0° (загроза упору в кронштейн понад 125°).
     *                  Драйвер перехоплює команди, клемпує їх до 10.0° та 125.0°, рятуючи механіку.
     * 3600 .. 4600 мс: Плавне повернення осей у вихідну нейтраль (90°, 90°).
     */
    for (uint32_t step = 0; step < 235; ++step) {
        sim_time_ms = step * DT_MS;
        const char *event_note = "";

        if (sim_time_ms == 100U) {
            servo_set_target_angle(&pan_servo, 40.0f);
            servo_set_target_angle(&tilt_servo, 30.0f);
            event_note = ">>> Команда осям: Pan -> 40.0°, Tilt -> 30.0° (Плавний розгін)";
        } else if (sim_time_ms == 1200U) {
            servo_set_target_angle(&pan_servo, 145.0f);
            servo_set_target_angle(&tilt_servo, 110.0f);
            event_note = ">>> Команда осям: Pan -> 145.0°, Tilt -> 110.0° (Сканування)";
        } else if (sim_time_ms == 2400U) {
            /* Тестова спроба перевищити межі шарніра */
            bool pan_ok = servo_set_target_angle(&pan_servo, -25.0f);
            bool tilt_ok = servo_set_target_angle(&tilt_servo, 160.0f);
            (void)pan_ok;
            (void)tilt_ok;
            event_note = "!!! АВАРІЙНИЙ ТЕСТ: Запит Pan -25° та Tilt 160° -> СОФТ-ЛІМІТИ АКТИВОВАНО!";
        } else if (sim_time_ms == 3600U) {
            servo_set_target_angle(&pan_servo, 90.0f);
            servo_set_target_angle(&tilt_servo, 90.0f);
            event_note = ">>> Повернення осей у нейтральне положення (90.0°, 90.0°)";
        }

        /* Неблокувальне оновлення траєкторій обох сервоприводів */
        servo_update(&pan_servo, DT_MS);
        servo_update(&tilt_servo, DT_MS);

        /* Розрахунок електричних параметрів шини */
        float i_pan = estimate_servo_current_ma(&pan_servo, true);
        float i_tilt = estimate_servo_current_ma(&tilt_servo, false);
        float i_total = i_pan + i_tilt;

        /* Падіння напруги на дротах живлення та внутрішньому опорі джерела (R_wire ~ 0.35 Ом) */
        float v_drop = (i_total / 1000.0f) * 0.35f;
        float v_bus = 5.00f - v_drop;

        /* Друк телеметрії кожні 120 мс або під час ключових подій */
        if ((sim_time_ms % 120U == 0U) || (event_note[0] != '\0')) {
            print_telemetry_row(sim_time_ms, &pan_servo, &tilt_servo, i_total, v_bus, event_note);
        }
    }

    printf("--------------------------------------------------------------------------------------------------------\n\n");

    /* ------------------------------------------------------------------------
     * ЕТАП 4: ТЕХНІЧНИЙ ПІДСУМОК ТА ПОРІВНЯЛЬНИЙ АНАЛІЗ
     * ------------------------------------------------------------------------ */
    printf("4. ПОРІВНЯЛЬНИЙ АНАЛІЗ: ПРЯМЕ СТУПІНЧАСТЕ КЕРУВАННЯ VS ПРОЦЕДУРНИЙ ДРАЙВЕР:\n");
    printf("========================================================================================================\n");
    printf(" Параметр                       | Пряме керування (Step / Delay)   | Процедурний драйвер з рампою та лімітами \n");
    printf("--------------------------------+----------------------------------+------------------------------------\n");
    printf(" Механічні упори (0° та 180°)   | Удар вала, зрізання зубів SG90   | Софт-ліміти гарантують буфер 5°..15° \n");
    printf(" Струм під час зміни позиції    | Сплеск блокування I_stall > 1.2 А| Плавний розгін, піковий струм < 320 мА \n");
    printf(" Стабільність шини живлення 5 В | Просідання < 4.0 В (Brown-Out)   | Стабільна напруга 4.88..4.98 В \n");
    printf(" Ресурс нейлонового редуктора   | Швидкий знос або злам шестерень  | Захист від ривка d²theta/dt² (довговічність)\n");
    printf(" Калібрування центрального кута | Перекіс качалки через крок шліца | Програмний trim_offset з точністю 1 мкс \n");
    printf(" Використання процесора         | Блокувальні затримки delay()     | 100%% неблокувальний код для суперциклу \n");
    printf(" Динамічна пам'ять (Heap)       | —                                | 0 байтів (повна відсутність malloc) \n");
    printf("========================================================================================================\n");

    return 0;
}
