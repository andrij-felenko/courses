#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "stm32f4xx.h"

// Перелік глобальних статусів диспетчера ініціалізації
typedef enum {
    INIT_ENGINE_IDLE = 0,
    INIT_ENGINE_RUNNING,
    INIT_ENGINE_SUCCESS,
    INIT_ENGINE_FAILED,
    INIT_ENGINE_DEGRADED
} init_engine_status_t;

// Типи функцій зворотного виклику для кроків послідовності
typedef bool (*init_action_fn)(void *ctx);
typedef bool (*init_poll_fn)(void *ctx);
typedef void (*init_rollback_fn)(void *ctx);

// Дескриптор одного етапу ініціалізації
typedef struct {
    const char       *name;             // Назва кроку для трасування та діагностики
    init_action_fn    action;           // Апаратна дія на старті кроку (може бути NULL)
    uint32_t          hold_delay_us;    // Захисна витримка перехідного процесу
    init_poll_fn      poll_condition;   // Предикат опитування готовності (може бути NULL)
    uint32_t          timeout_us;       // Граничний таймаут очікування умови
    init_rollback_fn  rollback;         // Функція безпечного відкату при збої
    bool              is_critical;      // Фатальність збою для системи
} init_step_t;

// Фази виконання окремого кроку всередині скінченного автомата
typedef enum {
    STEP_PHASE_ACTION = 0,
    STEP_PHASE_HOLD_DELAY,
    STEP_PHASE_POLLING
} step_phase_t;

// Контекст стану диспетчера
typedef struct {
    const init_step_t   *steps;
    size_t               total_steps;
    size_t               current_index;
    step_phase_t         phase;
    uint32_t             phase_start_ticks;
    uint32_t             poll_start_ticks;
    void                *user_context;
    init_engine_status_t status;
    uint32_t             failed_step_mask;
} init_engine_t;

// ── Апаратні допоміжні функції ──

static inline void dwt_timer_init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

static inline uint32_t dwt_get_cycles(void) {
    return DWT->CYCCNT;
}

static inline uint32_t us_to_dwt_ticks(uint32_t us) {
    return us * (SystemCoreClock / 1000000U);
}

static inline void watchdog_feed(void) {
    #if defined(IWDG)
    IWDG->KR = 0xAAAAU; // Оновлення незалежного сторожового таймера
    #endif
}

// ── Публічне API рушія ініціалізації ──

void init_engine_start(init_engine_t *eng, const init_step_t *steps, size_t count, void *ctx) {
    dwt_timer_init();
    eng->steps = steps;
    eng->total_steps = count;
    eng->current_index = 0;
    eng->phase = STEP_PHASE_ACTION;
    eng->phase_start_ticks = dwt_get_cycles();
    eng->poll_start_ticks = 0;
    eng->user_context = ctx;
    eng->status = (count > 0) ? INIT_ENGINE_RUNNING : INIT_ENGINE_SUCCESS;
    eng->failed_step_mask = 0;
}

init_engine_status_t init_engine_poll(init_engine_t *eng) {
    if (eng->status != INIT_ENGINE_RUNNING) {
        return eng->status;
    }

    watchdog_feed(); // Регулярне скидання вартівника без блокування

    if (eng->current_index >= eng->total_steps) {
        eng->status = (eng->failed_step_mask == 0) ? INIT_ENGINE_SUCCESS : INIT_ENGINE_DEGRADED;
        return eng->status;
    }

    const init_step_t *step = &eng->steps[eng->current_index];
    uint32_t now = dwt_get_cycles();

    switch (eng->phase) {
        case STEP_PHASE_ACTION: {
            if (step->action != NULL) {
                if (!step->action(eng->user_context)) {
                    // Апаратна дія повернула помилку: виклик відкату
                    if (step->rollback != NULL) {
                        step->rollback(eng->user_context);
                    }
                    eng->failed_step_mask |= (1U << eng->current_index);
                    if (step->is_critical) {
                        eng->status = INIT_ENGINE_FAILED;
                        return eng->status;
                    }
                    // Некритичний крок — перехід до наступного етапу
                    eng->current_index++;
                    eng->phase = STEP_PHASE_ACTION;
                    return eng->status;
                }
            }
            eng->phase_start_ticks = now;
            eng->phase = STEP_PHASE_HOLD_DELAY;
            break;
        }

        case STEP_PHASE_HOLD_DELAY: {
            uint32_t delay_ticks = us_to_dwt_ticks(step->hold_delay_us);
            if ((now - eng->phase_start_ticks) >= delay_ticks) {
                if (step->poll_condition != NULL) {
                    eng->poll_start_ticks = now;
                    eng->phase = STEP_PHASE_POLLING;
                } else {
                    // Фіксована витримка завершена, перевірка не потрібна
                    eng->current_index++;
                    eng->phase = STEP_PHASE_ACTION;
                }
            }
            break;
        }

        case STEP_PHASE_POLLING: {
            if (step->poll_condition(eng->user_context)) {
                // Умова готовності підтверджена
                eng->current_index++;
                eng->phase = STEP_PHASE_ACTION;
            } else {
                uint32_t timeout_ticks = us_to_dwt_ticks(step->timeout_us);
                if ((now - eng->poll_start_ticks) >= timeout_ticks) {
                    // Вичерпано таймаут очікування
                    if (step->rollback != NULL) {
                        step->rollback(eng->user_context);
                    }
                    eng->failed_step_mask |= (1U << eng->current_index);
                    if (step->is_critical) {
                        eng->status = INIT_ENGINE_FAILED;
                        return eng->status;
                    }
                    // Некритичний збій — продовження роботи у деградованому режимі
                    eng->current_index++;
                    eng->phase = STEP_PHASE_ACTION;
                }
            }
            break;
        }
    }

    return eng->status;
}

// ── Реалізація практичного сценарію ініціалізації плати ──

typedef struct {
    bool psu_good;
    bool i2c_bus_recovered;
    bool imu_online;
    bool flash_online;
} board_system_ctx_t;

// Крок 1: Увімкнення стабілізатора живлення 3.3V
static bool act_power_rail_on(void *ctx) {
    (void)ctx;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOCEN;
    GPIOC->BSRR = GPIO_BSRR_BS13; // Високий рівень на ключ Enable
    GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODER13_Msk) | (1U << GPIO_MODER_MODER13_Pos);
    return true;
}

static bool poll_power_rail_ready(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    board->psu_good = true;
    return true;
}

static void rb_power_rail_fault(void *ctx) {
    (void)ctx;
    GPIOC->BSRR = GPIO_BSRR_BR13; // Аварійне зняття живлення
}

// Крок 2: Розблокування шини I2C (Bus Recovery)
static bool act_i2c_bus_recovery(void *ctx) {
    (void)ctx;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    // Налаштування PB8 (SCL) та PB9 (SDA) як виходи Open Drain
    GPIOB->MODER = (GPIOB->MODER & ~(GPIO_MODER_MODER8_Msk | GPIO_MODER_MODER9_Msk)) |
                   (1U << GPIO_MODER_MODER8_Pos) | (1U << GPIO_MODER_MODER9_Pos);
    GPIOB->OTYPER |= GPIO_OTYPER_OT_8 | GPIO_OTYPER_OT_9;
    GPIOB->BSRR = GPIO_BSRR_BS8 | GPIO_BSRR_BS9;

    // Генерація 9 імпульсів для звільнення лінії SDA
    for (int i = 0; i < 9; i++) {
        GPIOB->BSRR = GPIO_BSRR_BR8; // SCL = 0
        for (volatile int d = 0; d < 50; d++) __NOP();
        GPIOB->BSRR = GPIO_BSRR_BS8; // SCL = 1
        for (volatile int d = 0; d < 50; d++) __NOP();
    }
    return true;
}

static bool poll_i2c_bus_free(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    bool sda_high = (GPIOB->IDR & GPIO_IDR_IDR_9) != 0;
    board->i2c_bus_recovered = sda_high;
    return sda_high;
}

static void rb_i2c_fault(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    board->i2c_bus_recovered = false;
}

// Крок 3: Апаратне скидання акселерометра IMU
static bool act_imu_reset_pulse(void *ctx) {
    (void)ctx;
    GPIOC->BSRR = GPIO_BSRR_BR4; // nRST = LOW
    GPIOC->MODER = (GPIOC->MODER & ~GPIO_MODER_MODER4_Msk) | (1U << GPIO_MODER_MODER4_Pos);
    return true;
}

static bool act_imu_release_reset(void *ctx) {
    (void)ctx;
    GPIOC->BSRR = GPIO_BSRR_BS4; // nRST = HIGH (Release)
    return true;
}

static bool poll_imu_whoami(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    // Імітація обміну по SPI: перевірка відповіді 0x75
    board->imu_online = true;
    return true;
}

static void rb_imu_isolate(void *ctx) {
    board_system_ctx_t *board = (board_system_ctx_t *)ctx;
    board->imu_online = false;
    // Переведення виводів датчика у високий опір
    GPIOC->MODER &= ~GPIO_MODER_MODER4_Msk;
}

// Таблиця конфігурації етапів ініціалізації обладнання
static const init_step_t g_system_init_sequence[] = {
    {
        .name = "POWER_RAIL_3V3_ENABLE",
        .action = act_power_rail_on,
        .hold_delay_us = 10000U, // 10 мс на наростання напруги V_DD
        .poll_condition = poll_power_rail_ready,
        .timeout_us = 5000U,
        .rollback = rb_power_rail_fault,
        .is_critical = true
    },
    {
        .name = "I2C_BUS_RECOVERY",
        .action = act_i2c_bus_recovery,
        .hold_delay_us = 2000U,  // 2 мс стабілізації ліній
        .poll_condition = poll_i2c_bus_free,
        .timeout_us = 3000U,
        .rollback = rb_i2c_fault,
        .is_critical = false
    },
    {
        .name = "IMU_ASSERT_RESET",
        .action = act_imu_reset_pulse,
        .hold_delay_us = 15000U, // 15 мс утримання апаратного скидання
        .poll_condition = NULL,
        .timeout_us = 0,
        .rollback = NULL,
        .is_critical = false
    },
    {
        .name = "IMU_BOOT_AND_PROBE",
        .action = act_imu_release_reset,
        .hold_delay_us = 25000U, // 25 мс очікування завантаження ROM чипа
        .poll_condition = poll_imu_whoami,
        .timeout_us = 10000U,
        .rollback = rb_imu_isolate,
        .is_critical = false
    }
};

void run_c99_bringup_task(void) {
    board_system_ctx_t board_state = {0};
    init_engine_t engine;

    init_engine_start(&engine, g_system_init_sequence,
                      sizeof(g_system_init_sequence) / sizeof(g_system_init_sequence[0]),
                      &board_state);

    while (init_engine_poll(&engine) == INIT_ENGINE_RUNNING) {
        // Фонова робота: миготіння світлодіодом, очікування подій
        __NOP();
    }

    if (engine.status == INIT_ENGINE_SUCCESS) {
        // Усі вузли готові до штатної роботи
    } else if (engine.status == INIT_ENGINE_DEGRADED) {
        // Запуск приладу з відключеними другорядними сенсорами
    } else {
        // Аварійна зупинка: критичний збій живлення
    }
}
