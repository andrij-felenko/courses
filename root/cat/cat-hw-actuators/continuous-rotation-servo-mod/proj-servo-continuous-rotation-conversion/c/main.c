/**
 * @file main.c
 * @brief Демонстрація роботи процедурного драйвера сервопривода постійного обертання (C99).
 *
 * Програма ілюструє:
 * 1. Низькорівневу конфігурацію апаратного ШІМ-таймера мікроконтролера (50 Гц, дискретність 1 мкс).
 * 2. Проблему асиметрії внутрішнього дільника напруги та самочинного прокручування вала (creeping).
 * 3. Програмне калібрування тривалості нейтрального імпульсу спокою та фіксацію мертвої зони (deadband).
 * 4. Неблокувальний лінійний рампінг швидкості в суперциклі:
 *    - Плавний пуск (soft-start) без струмових кидків і просідання напруги живлення;
 *    - Контрольований реверс із безпечним проходженням через нуль для захисту зубців редуктора;
 *    - Плавне гальмування до повної зупинки (soft-stop);
 *    - Динамічну компенсацію температурного дрейфу дільника під навантаженням.
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include "continuous_servo.h"

/*
 * ============================================================================
 * АПАРАТНИЙ РІВЕНЬ: ЕМУЛЯЦІЯ РЕГІСТРІВ ШІМ-ТАЙМЕРА МІКРОКОНТРОЛЕРА
 * ============================================================================
 * Структура моделює стандартний периферійний таймер загального призначення
 * (наприклад, TIM2/TIM3 у STM32, Timer1 в AVR або MCPWM в ESP32).
 */
typedef struct {
    volatile uint32_t CR1;   /**< Control Register 1: біт 0 (CEN) — дозвіл лічби */
    volatile uint32_t PSC;   /**< Prescaler Register: подільник вхідної тактової частоти */
    volatile uint32_t ARR;   /**< Auto-Reload Register: значення переповнення лічильника (період) */
    volatile uint32_t CCR1;  /**< Capture/Compare Register 1: тривалість активного імпульсу */
    volatile uint32_t CCER;  /**< Capture/Compare Enable Register: дозвіл виходу каналу */
} mcu_timer_hw_t;

/**
 * @brief Налаштування апаратного ШІМ-таймера на стандартну частоту 50 Гц (період 20 мс)
 *
 * @param timer Покажчик на структуру регістрів таймера.
 * @param timer_clock_hz Вхідна частота тактування таймера від шини (наприклад, 16 000 000 Гц).
 * @param pwm_freq_hz Бажана частота ШІМ для сервопривода (50 Гц).
 */
static void mcu_timer_pwm_init(mcu_timer_hw_t *timer, uint32_t timer_clock_hz, uint32_t pwm_freq_hz)
{
    /*
     * 1. Налаштування переддільника (PSC):
     *    Для забезпечення зручного та точного завдання тривалості імпульсу в мікросекундах
     *    встановлюємо тактову частоту лічильника рівною 1 МГц (1 такт = 1 мкс):
     *      f_cnt = timer_clock_hz / (PSC + 1) = 1 000 000 Гц
     *      PSC = (timer_clock_hz / 1 000 000) - 1
     *    Для частоти шини 16 МГц: PSC = (16 000 000 / 1 000 000) - 1 = 15.
     */
    uint32_t timer_cnt_freq = 1000000UL;
    timer->PSC = (timer_clock_hz / timer_cnt_freq) - 1UL;

    /*
     * 2. Розрахунок періоду ШІМ (ARR):
     *    Період повторення сервоімпульсів T = 20 мс (50 Гц).
     *    При частоті лічильника 1 МГц період становить 20 000 відліків:
     *      ARR = (f_cnt / pwm_freq_hz) - 1
     *      ARR = (1 000 000 / 50) - 1 = 19 999 відліків (від 0 до 19999).
     */
    timer->ARR = (timer_cnt_freq / pwm_freq_hz) - 1UL;

    /* 3. Початкова шпаруватість — стандартний нейтральний імпульс 1500 мкс */
    timer->CCR1 = 1500UL;

    /* 4. Увімкнення виходу каналу ШІМ (CC1E = 1) */
    timer->CCER = 0x0001UL;

    /* 5. Запуск лічильника таймера (CEN = 1) */
    timer->CR1 = 0x0001UL;
}

/**
 * @brief Апаратний зворотний виклик для запису тривалості імпульсу в регістр таймера
 */
static void mcu_timer_pwm_write(uint32_t pulse_us, void *user_data)
{
    mcu_timer_hw_t *timer = (mcu_timer_hw_t *)user_data;
    if (timer != NULL) {
        timer->CCR1 = pulse_us;
    }
}

/*
 * ============================================================================
 * ФІЗИЧНА МОДЕЛЬ СЕРВОПРИВОДА З МОДИФІКАЦІЄЮ НА ПОСТІЙНЕ ОБЕРТАННЯ
 * ============================================================================
 * У сервоприводі постійного обертання потенціометр зворотного зв'язку замінено
 * на дільник із двох резисторів (номінально 2.2 кОм). Через технологічний розкид
 * опорів (+/-1.5%) напруга середньої точки зміщена, тому фізична нейтраль
 * спокою цього екземпляра зміщена на +18 мкс (1518 мкс замість 1500 мкс).
 */
#define SERVO_PHYSICAL_NEUTRAL_US       1518U   /**< Реальна фізична точка спокою вала */
#define SERVO_INTERNAL_DEADBAND_US      15U     /**< Внутрішня апаратна мертва зона мікросхеми серво */
#define SERVO_MAX_NO_LOAD_RPM           60.0f   /**< Максимальна швидкість холостого ходу (об/хв) */

/**
 * @brief Розрахунок фізичної швидкості обертання вала в об/хв для поточної тривалості імпульсу
 */
static float calculate_physical_rpm(uint32_t pulse_us, uint16_t physical_neutral_us)
{
    int32_t delta = (int32_t)pulse_us - (int32_t)physical_neutral_us;

    /* Якщо імпульс потрапляє у внутрішню мертву зону компаратора — вал нерухомий */
    if (abs(delta) <= (int32_t)SERVO_INTERNAL_DEADBAND_US) {
        return 0.0f;
    }

    if (delta > 0) {
        float active_delta = (float)(delta - (int32_t)SERVO_INTERNAL_DEADBAND_US);
        float max_delta = (float)(CONTINUOUS_SERVO_DEFAULT_MAX_PULSE_US - physical_neutral_us - SERVO_INTERNAL_DEADBAND_US);
        float norm = active_delta / max_delta;
        if (norm > 1.0f) norm = 1.0f;
        return norm * SERVO_MAX_NO_LOAD_RPM;
    } else {
        float active_delta = (float)(-delta - (int32_t)SERVO_INTERNAL_DEADBAND_US);
        float max_delta = (float)(physical_neutral_us - SERVO_INTERNAL_DEADBAND_US - CONTINUOUS_SERVO_DEFAULT_MIN_PULSE_US);
        float norm = active_delta / max_delta;
        if (norm > 1.0f) norm = 1.0f;
        return -norm * SERVO_MAX_NO_LOAD_RPM;
    }
}

/**
 * @brief Оцінка споживаного струму (мА) та напруги живлення (В) на шині 5 В
 */
static void estimate_electrical_metrics(float current_speed, float rpm, float *out_current_ma, float *out_bus_voltage_v)
{
    if (fabsf(rpm) < 0.1f) {
        /* Струм спокою схеми керування (H-міст знеструмлений) */
        *out_current_ma = 6.5f;
        *out_bus_voltage_v = 5.00f;
    } else {
        /* Струм пропорційний навантаженню та швидкості: базовий холостий хід ~120 мА + динамічний */
        float load_factor = fabsf(current_speed);
        *out_current_ma = 120.0f + load_factor * 180.0f;

        /* Внутрішній опір джерела та дротів R_wire ~ 0.25 Ом -> просідання напруги */
        float v_drop = (*out_current_ma / 1000.0f) * 0.25f;
        *out_bus_voltage_v = 5.00f - v_drop;
    }
}

/**
 * @brief Друк рядка таблиці телеметрії
 */
static void print_telemetry_row(uint32_t time_ms,
                                const continuous_servo_t *servo,
                                float physical_rpm,
                                float current_ma,
                                float bus_v,
                                const char *note)
{
    float duty_pct = ((float)servo->current_pulse_us / 20000.0f) * 100.0f;
    printf(" [%4u мс] | %-18s | %+5.2f | %+5.2f | %4u мкс | %5.2f%% | %+5.1f | %5.1f мА | %4.2f В | %s\n",
           (unsigned int)time_ms,
           continuous_servo_state_name(servo->state),
           continuous_servo_get_target_speed(servo),
           continuous_servo_get_current_speed(servo),
           servo->current_pulse_us,
           (double)duty_pct,
           (double)physical_rpm,
           (double)current_ma,
           (double)bus_v,
           note);
}

int main(void)
{
    printf("========================================================================================================\n");
    printf("     ПРОЦЕДУРНИЙ ДРАЙВЕР СЕРВОПРИВОДА ПОСТІЙНОГО ОБЕРТАННЯ З АПАРАТНИМ ШІМ 50 Гц (C99)                  \n");
    printf("========================================================================================================\n\n");

    /* ------------------------------------------------------------------------
     * ЕТАП 1: НАЛАШТУВАННЯ АПАРАТНОГО ШІМ-ТАЙМЕРА ТА ІНІЦІАЛІЗАЦІЯ ДРАЙВЕРА
     * ------------------------------------------------------------------------ */
    mcu_timer_hw_t timer_hw;
    const uint32_t SYSTEM_CLOCK_HZ = 16000000UL; /* Тактова частота шини таймера: 16 МГц */
    const uint32_t SERVO_PWM_FREQ_HZ = 50UL;     /* Стандартна частота сервоприводів: 50 Гц */

    mcu_timer_pwm_init(&timer_hw, SYSTEM_CLOCK_HZ, SERVO_PWM_FREQ_HZ);

    printf("1. НАЛАШТУВАННЯ АПАРАТНОГО ТАЙМЕРА МІКРОКОНТРОЛЕРА:\n");
    printf("   - Вхідна тактова частота шини: %u Гц\n", (unsigned int)SYSTEM_CLOCK_HZ);
    printf("   - Переддільник PSC:            %u (частота лічильника = 1.0 МГц, 1 відлік = 1 мкс)\n",
           (unsigned int)timer_hw.PSC);
    printf("   - Регістр автоперезавантаження ARR: %u (період ШІМ = 20 000 мкс = 20.0 мс, 50 Гц)\n",
           (unsigned int)timer_hw.ARR);
    printf("   - Початковий регістр порівняння CCR1: %u мкс (стандартна нейтраль)\n\n",
           (unsigned int)timer_hw.CCR1);

    /* Конфігурація екземпляра сервопривода */
    continuous_servo_config_t config = {
        .calib = {
            .min_pulse_us     = CONTINUOUS_SERVO_DEFAULT_MIN_PULSE_US,
            .max_pulse_us     = CONTINUOUS_SERVO_DEFAULT_MAX_PULSE_US,
            .neutral_pulse_us = CONTINUOUS_SERVO_DEFAULT_NEUTRAL_US,
            .deadband_us      = CONTINUOUS_SERVO_DEFAULT_DEADBAND_US,
            .trim_offset_us   = 0 /* Початково зміщення невідоме */
        },
        .ramp = {
            .accel_rate       = CONTINUOUS_SERVO_DEFAULT_ACCEL_RATE,
            .decel_rate       = CONTINUOUS_SERVO_DEFAULT_DECEL_RATE,
            .deadband_speed   = CONTINUOUS_SERVO_DEFAULT_DEADBAND_SPEED
        },
        .pwm_write = mcu_timer_pwm_write,
        .user_data = &timer_hw
    };

    continuous_servo_t servo;
    if (!continuous_servo_init(&servo, &config)) {
        printf("[ПОМИЛКА]: Не вдалося ініціалізувати сервопривід!\n");
        return 1;
    }

    printf("2. ДЕМОНСТРАЦІЯ АСИМЕТРІЇ ВНУТРІШНЬОГО ДІЛЬНИКА ТА САМОЧИННОГО ДРЕЙФУ (CREEPING):\n");
    printf("   - Фізична точка спокою цього екземпляра через похибку резисторів: %u мкс\n", SERVO_PHYSICAL_NEUTRAL_US);
    printf("   - Сигнал за замовчуванням:                                       %u мкс\n", servo.current_pulse_us);
    printf("   - Відхилення від фізичної нейтралі:                              %+d мкс\n",
           (int)servo.current_pulse_us - (int)SERVO_PHYSICAL_NEUTRAL_US);

    float uncalibrated_rpm = calculate_physical_rpm(servo.current_pulse_us, SERVO_PHYSICAL_NEUTRAL_US);
    printf("   -> Наслідок без калібрування: вал САМОЧИННО ПРОКРУЧУЄТЬСЯ зі швидкістю %.1f об/хв!\n",
           (double)uncalibrated_rpm);
    printf("   -> Внутрішній компаратор виходить за межі deadband (%u мкс), H-міст створює паразитно шум і нагрів.\n\n",
           SERVO_INTERNAL_DEADBAND_US);

    /* ------------------------------------------------------------------------
     * ЕТАП 2: ПРОГРАМНЕ КАЛІБРУВАННЯ НЕЙТРАЛІ
     * ------------------------------------------------------------------------ */
    printf("3. ВИКОНАННЯ ПРОГРАМНОГО КАЛІБРУВАННЯ НЕЙТРАЛІ:\n");
    bool calib_ok = continuous_servo_calibrate_neutral(&servo, SERVO_PHYSICAL_NEUTRAL_US);
    printf("   - Виклик continuous_servo_calibrate_neutral(&servo, %u) -> %s\n",
           SERVO_PHYSICAL_NEUTRAL_US, calib_ok ? "УСПІШНО" : "ПОМИЛКА");
    printf("   - Розраховано програмний зсув trim_offset_us: %+d мкс\n",
           continuous_servo_get_neutral_trim(&servo));
    printf("   - Ефективна нейтраль приводу:                 %u мкс\n",
           continuous_servo_get_effective_neutral(&servo));
    printf("   - Нове значення в регістрі CCR1 таймера:      %u мкс\n",
           (unsigned int)timer_hw.CCR1);

    float calibrated_rpm = calculate_physical_rpm(servo.current_pulse_us, SERVO_PHYSICAL_NEUTRAL_US);
    printf("   -> Результат: фізична швидкість вала = %.1f об/хв (ВАЛ ПОВНІСТЮ ЗУПИНЕНО, СПОКІЙ ГАРАНТОВАНО).\n\n",
           (double)calibrated_rpm);

    /* ------------------------------------------------------------------------
     * ЕТАП 3: ГОЛОВНИЙ СУПЕРЦИКЛ — ДЕМОНСТРАЦІЯ РАМПІНГУ, РЕВЕРСУ Й ЗУПИНКИ
     * ------------------------------------------------------------------------ */
    printf("4. ДЕМОНСТРАЦІЯ НЕБЛОКУВАЛЬНОГО КЕРУВАННЯ В СУПЕРЦИКЛІ (КРОК КВАНТУВАННЯ dt = 20 мс):\n");
    printf("--------------------------------------------------------------------------------------------------------\n");
    printf("   ЧАС      | СТАН ПРИВОДУ       | ЦІЛЬ  | ФАКТ  |  ШІМ-ІМПУЛЬС  | ШПАРУВ. | ОБ/ХВ |  СТРУМ   | НАПРУГА | ПОДІЯ ТА ФІЗИЧНИЙ СТАН\n");
    printf("--------------------------------------------------------------------------------------------------------\n");

    const uint32_t DT_MS = 20U; /* Крок планувальника відповідає періоду ШІМ 50 Гц (20 мс) */
    uint32_t current_time_ms = 0U;
    uint16_t active_physical_neutral = SERVO_PHYSICAL_NEUTRAL_US;

    /* Сценарій демонстрації:
     * 0 .. 100 мс:    Спокій на нейтралі
     * 100 .. 800 мс:  Команда +0.80 (розгін вперед, soft-start, захист редуктора)
     * 800 .. 1200 мс: Крейсерський рух +0.80
     * 1200 .. 2200 мс: Команда -0.60 (контрольований реверс через нуль)
     * 2200 .. 2600 мс: Крейсерський рух -0.60
     * 2600 .. 3200 мс: Команда 0.00 (плавне гальмування до спокою)
     * 3200 .. 3500 мс: Температурний дрейф +8 мкс та динамічна компенсація trim
     */
    for (uint32_t step = 0; step < 175; ++step) {
        current_time_ms = step * DT_MS;
        const char *event_note = "";

        /* Зміна цільових команд у задані моменти часу */
        if (current_time_ms == 100U) {
            continuous_servo_set_speed(&servo, 0.80f);
            event_note = ">>> Команда швидкості +0.80 (Плавний пуск)";
        } else if (current_time_ms == 800U) {
            event_note = "--- Досягнуто крейсерської швидкості +0.80";
        } else if (current_time_ms == 1200U) {
            continuous_servo_set_speed(&servo, -0.60f);
            event_note = ">>> Команда реверсу -0.60 (Гальмування до 0)";
        } else if (current_time_ms == 2200U) {
            event_note = "--- Досягнуто крейсерської швидкості -0.60";
        } else if (current_time_ms == 2600U) {
            continuous_servo_stop(&servo);
            event_note = ">>> Команда повної зупинки вала (Soft-Stop)";
        } else if (current_time_ms == 3200U) {
            /* Симуляція нагріву двигуна та мікросхеми: фізична нейтраль зміщується на +8 мкс */
            active_physical_neutral += 8U;
            event_note = "!!! Нагрів схеми: дрейф фізичної нейтралі до 1526 мкс";
        } else if (current_time_ms == 3300U) {
            /* Динамічна корекція зсуву нейтралі через trim */
            continuous_servo_set_neutral_trim(&servo, (int16_t)(active_physical_neutral - CONTINUOUS_SERVO_DEFAULT_NEUTRAL_US));
            event_note = ">>> Компенсація trim_offset = +26 мкс (Усунення дрейфу)";
        }

        /* Періодичний неблокувальний крок драйвера */
        continuous_servo_update(&servo, DT_MS);

        /* Розрахунок фізичних метрик для моніторингу */
        float physical_rpm = calculate_physical_rpm(servo.current_pulse_us, active_physical_neutral);
        float current_ma, bus_voltage_v;
        estimate_electrical_metrics(servo.current_speed, physical_rpm, &current_ma, &bus_voltage_v);

        /* Вибірковий вивід для збереження читабельності журналу (кожні 100 мс або під час ключових подій) */
        if ((current_time_ms % 100U == 0U) || (event_note[0] != '\0')) {
            print_telemetry_row(current_time_ms, &servo, physical_rpm, current_ma, bus_voltage_v, event_note);
        }
    }

    printf("--------------------------------------------------------------------------------------------------------\n\n");

    /* ------------------------------------------------------------------------
     * ЕТАП 4: ТЕХНІЧНЕ ПОРІВНЯННЯ ТА ПІДСУМКИ
     * ------------------------------------------------------------------------ */
    printf("5. ПОРІВНЯЛЬНИЙ АНАЛІЗ: ПРЯМЕ СТУПІНЧАСТЕ КЕРУВАННЯ VS НАШ ПРОЦЕДУРНИЙ ДРАЙВЕР:\n");
    printf("========================================================================================================\n");
    printf(" Параметр                       | Пряме ступінчасте перемикання    | Драйвер з калібруванням і рампінгом \n");
    printf("--------------------------------+----------------------------------+------------------------------------\n");
    printf(" Стійкість точки зупинки (0 RPM)| Дрейф, спонтанне прокручування   | Абсолютний спокій (deadband clamped)\n");
    printf(" Піковий пусковий струм (Inrush)| 1800..2500 мА (кидок блокування) | 260..300 мА (плавне наростання)\n");
    printf(" Просідання шини живлення 5 В   | До 3.4 В (ризик перезавантаження)| Не більше 4.93 В (стабільна робота)\n");
    printf(" Ударні навантаження в редукторі| Зрізання зубців мікрошестерень   | Плавний розгін dV/dt (збереження зубців)\n");
    printf(" Поведінка під час реверсу      | Подвійний кидок проти-ЕРС        | Зупинка в 0 -> перехід -> плавний хід\n");
    printf(" Температурний дрейф схеми      | Втрата нейтралі через 3-5 хв     | Програмний trim усуває зсув дільника\n");
    printf(" Пам'ять мікроконтролера        | —                                | 0 байтів динамічної пам'яті (без malloc)\n");
    printf("========================================================================================================\n");

    return 0;
}
