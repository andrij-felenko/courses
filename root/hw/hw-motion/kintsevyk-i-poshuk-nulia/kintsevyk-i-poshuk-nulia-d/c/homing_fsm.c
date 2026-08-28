/* 
 * homing_fsm.h / homing_fsm.c
 * Промислова неблокуюча реалізація автомата пошуку нуля на мові C
 */

#include <stdint.h>
#include <stdbool.h>

/* Стан автомата хомінгу */
typedef enum {
    HOMING_STATE_IDLE = 0,
    HOMING_STATE_START,
    HOMING_STATE_FAST_SEEK,
    HOMING_STATE_FAST_DECEL,
    HOMING_STATE_RETRACT,
    HOMING_STATE_SLOW_APPROACH,
    HOMING_STATE_LATCH,
    HOMING_STATE_PARK,
    HOMING_STATE_DONE,
    HOMING_STATE_FAULT
} HomingState;

/* Коди помилок калібрування */
typedef enum {
    HOMING_ERR_NONE = 0,
    HOMING_ERR_TIMEOUT,
    HOMING_ERR_OVERTRAVEL,
    HOMING_ERR_SENSOR_STUCK,
    HOMING_ERR_ESTOP
} HomingError;

/* Конфігурація осі */
typedef struct {
    float fast_feed_mm_s;       /* Швидкість швидкого пошуку (50-100 мм/с) */
    float slow_feed_mm_s;       /* Швидкість точного доїзду (1-3 мм/с) */
    float retract_dist_mm;      /* Дистанція відкату назад (2-5 мм) */
    float park_dist_mm;         /* Зазор паркування від контакту (1 мм) */
    float max_travel_mm;        /* Максимальний хід осі для таймауту (мм) */
    float steps_per_mm;         /* Кількість мікрокроків на 1 мм переміщення */
    bool  active_low;           /* true = NC контакт (LOW при контакті) */
} HomingConfig;

/* Контекст стану осі */
typedef struct {
    HomingState  state;
    HomingError  error;
    HomingConfig config;
    int32_t      current_step;      /* Поточний лічильник кроків */
    int32_t      step_limit;        /* Ліміт кроків до таймауту */
    int32_t      target_step;       /* Цільова позиція для відкату/паркування */
    uint32_t     step_interval_us;  /* Інтервал таймера між кроками */
    uint32_t     last_step_time_us; /* Час останнього згенерованого кроку */
} HomingContext;

/* Інтерфейс драйвера обладнання */
typedef struct {
    bool (*read_endstop)(void);
    void (*step)(int direction);
    uint32_t (*get_time_us)(void);
} HomingHal;

/* Ініціалізація контексту */
void homing_init(HomingContext *ctx, const HomingConfig *cfg) {
    if (!ctx || !cfg) return;
    ctx->state = HOMING_STATE_IDLE;
    ctx->error = HOMING_ERR_NONE;
    ctx->config = *cfg;
    ctx->current_step = 0;
    ctx->step_limit = 0;
    ctx->target_step = 0;
    ctx->step_interval_us = 1000;
    ctx->last_step_time_us = 0;
}

/* Запуск процедури калібрування */
void homing_start(HomingContext *ctx) {
    if (!ctx) return;
    ctx->state = HOMING_STATE_START;
    ctx->error = HOMING_ERR_NONE;
    ctx->current_step = 0;
}

/* Зчитування логічного стану датчика з урахуванням конфігурації NC/NO */
static inline bool is_endstop_triggered(const HomingContext *ctx, const HomingHal *hal) {
    bool raw = hal->read_endstop();
    return ctx->config.active_low ? !raw : raw;
}

/* Розрахунок мікросекундного інтервалу між імпульсами для заданої швидкості */
static inline uint32_t speed_to_interval_us(float speed_mm_s, float steps_per_mm) {
    if (speed_mm_s <= 0.001f) speed_mm_s = 0.001f;
    float steps_per_sec = speed_mm_s * steps_per_mm;
    return (uint32_t)(1000000.0f / steps_per_sec);
}

/* 
 * Головна неблокуюча функція опитування автомата.
 * Викликається у циклі планувальника задач або періодичному таймері.
 */
void homing_poll(HomingContext *ctx, const HomingHal *hal) {
    if (!ctx || !hal || ctx->state == HOMING_STATE_IDLE || ctx->state == HOMING_STATE_DONE || ctx->state == HOMING_STATE_FAULT) {
        return;
    }

    uint32_t now = hal->get_time_us();

    switch (ctx->state) {
        case HOMING_STATE_START:
            /* Перевірка: якщо датчик уже затиснутий на старті, треба одразу робити відкат */
            if (is_endstop_triggered(ctx, hal)) {
                ctx->state = HOMING_STATE_RETRACT;
                ctx->step_interval_us = speed_to_interval_us(ctx->config.fast_feed_mm_s, ctx->config.steps_per_mm);
                ctx->target_step = ctx->current_step + (int32_t)(ctx->config.retract_dist_mm * ctx->config.steps_per_mm);
            } else {
                ctx->state = HOMING_STATE_FAST_SEEK;
                ctx->step_interval_us = speed_to_interval_us(ctx->config.fast_feed_mm_s, ctx->config.steps_per_mm);
                /* Захисний ліміт: 120% від максимальної довжини осі */
                ctx->step_limit = (int32_t)(ctx->config.max_travel_mm * 1.2f * ctx->config.steps_per_mm);
            }
            ctx->last_step_time_us = now;
            break;

        case HOMING_STATE_FAST_SEEK:
            /* Крокуємо до кінцевика з високою швидкістю */
            if (now - ctx->last_step_time_us >= ctx->step_interval_us) {
                ctx->last_step_time_us = now;
                
                if (is_endstop_triggered(ctx, hal)) {
                    /* Кінцевик знайдено: переходимо до відкату */
                    ctx->state = HOMING_STATE_RETRACT;
                    ctx->step_interval_us = speed_to_interval_us(ctx->config.fast_feed_mm_s * 0.5f, ctx->config.steps_per_mm);
                    ctx->target_step = ctx->current_step + (int32_t)(ctx->config.retract_dist_mm * ctx->config.steps_per_mm);
                } else {
                    hal->step(-1); /* Рух у напрямку від'ємних координат (до 0) */
                    ctx->current_step--;
                    
                    /* Контроль таймауту/перевищення дистанції */
                    if (-ctx->current_step > ctx->step_limit) {
                        ctx->state = HOMING_STATE_FAULT;
                        ctx->error = HOMING_ERR_OVERTRAVEL;
                    }
                }
            }
            break;

        case HOMING_STATE_RETRACT:
            /* Відкат назад для виходу із зони механічного гістерезису */
            if (now - ctx->last_step_time_us >= ctx->step_interval_us) {
                ctx->last_step_time_us = now;

                if (ctx->current_step < ctx->target_step) {
                    hal->step(+1); /* Рух у додатному напрямку (від датчика) */
                    ctx->current_step++;
                } else {
                    /* Відкат завершено. Перевіряємо, чи датчик дійсно розімкнувся */
                    if (is_endstop_triggered(ctx, hal)) {
                        ctx->state = HOMING_STATE_FAULT;
                        ctx->error = HOMING_ERR_SENSOR_STUCK;
                    } else {
                        /* Переходимо до прецизійного повільного доїзду */
                        ctx->state = HOMING_STATE_SLOW_APPROACH;
                        ctx->step_interval_us = speed_to_interval_us(ctx->config.slow_feed_mm_s, ctx->config.steps_per_mm);
                        ctx->step_limit = (int32_t)(ctx->config.retract_dist_mm * 2.0f * ctx->config.steps_per_mm);
                    }
                }
            }
            break;

        case HOMING_STATE_SLOW_APPROACH:
            /* Прецизійний доїзд на швидкості 1-3 мм/с */
            if (now - ctx->last_step_time_us >= ctx->step_interval_us) {
                ctx->last_step_time_us = now;

                if (is_endstop_triggered(ctx, hal)) {
                    /* ТОЧНА ТОЧКА НУЛЯ ЗНАЙДЕНА */
                    ctx->state = HOMING_STATE_LATCH;
                } else {
                    hal->step(-1);
                    ctx->current_step--;

                    if (ctx->target_step - ctx->current_step > ctx->step_limit) {
                        ctx->state = HOMING_STATE_FAULT;
                        ctx->error = HOMING_ERR_TIMEOUT;
                    }
                }
            }
            break;

        case HOMING_STATE_LATCH:
            /* Фіксація бази: поточний лічильник кроків обнуляється */
            ctx->current_step = 0;
            ctx->target_step = (int32_t)(ctx->config.park_dist_mm * ctx->config.steps_per_mm);
            ctx->step_interval_us = speed_to_interval_us(ctx->config.fast_feed_mm_s * 0.5f, ctx->config.steps_per_mm);
            ctx->state = HOMING_STATE_PARK;
            break;

        case HOMING_STATE_PARK:
            /* Від'їзд у робочу зону на зазор безпеки (1 мм) */
            if (now - ctx->last_step_time_us >= ctx->step_interval_us) {
                ctx->last_step_time_us = now;

                if (ctx->current_step < ctx->target_step) {
                    hal->step(+1);
                    ctx->current_step++;
                } else {
                    /* ХОМІНГ УСПІШНО ЗАВЕРШЕНО */
                    ctx->state = HOMING_STATE_DONE;
                }
            }
            break;

        default:
            ctx->state = HOMING_STATE_FAULT;
            ctx->error = HOMING_ERR_TIMEOUT;
            break;
    }
}
