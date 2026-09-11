#include "gearmotor_driver.h"
#include <stddef.h>

/*
 * ============================================================================
 * НИЗЬКОРІВНЕВИЙ ШАР АПАРАТНОГО ТАЙМЕРА ТА DEAD-TIME
 * ============================================================================
 *
 * Драйвер керує повним H-мостом через комплементарні виходи апаратного таймера:
 *   - Канал 1: High-Side A (прямий) та Low-Side A (інверсний комплементарний)
 *   - Канал 2: High-Side B (прямий) та Low-Side B (інверсний комплементарний)
 *
 * Апаратний генератор захисного часу (Dead-Time Generator, DTG):
 * При перемиканні плеча напівмоста транзистор, що закривається, потребує часу
 * на розряд ємності затвора (t_off). Якщо в цей момент відкрити зустрічний транзистор,
 * виникне пряме коротке замикання між шиною 6 В та GND (shoot-through).
 * Генератор dead-time автоматично додає затримку t_dead = dead_time_counts * T_clock
 * перед кожним увімкненням чергового ключа плеча.
 */

typedef struct {
    uint32_t cr1;     /**< Регістр керування таймером (увімкнення лічильника) */
    uint32_t arr;     /**< Регістр автоперезавантаження (період ШІМ) */
    uint32_t ccr1;    /**< Регістр порівняння напівмоста A (шпаруватість каналу 1) */
    uint32_t ccr2;    /**< Регістр порівняння напівмоста B (шпаруватість каналу 2) */
    uint32_t bdtr;    /**< Регістр генератора dead-time та аварійного відсікання */
    uint32_t ccer;    /**< Регістр увімкнення прямих та комплементарних виходів */
} timer_hardware_t;

/* Внутрішня структура регістрів таймера мікроконтролера */
static timer_hardware_t s_hw_tim;

/* Бітові прапорці конфігурації виходів у регістрі CCER */
#define TIM_CCER_CH1_EN      (1U << 0)  /**< High-Side напівмоста A увімкнено */
#define TIM_CCER_CH1N_EN     (1U << 2)  /**< Low-Side напівмоста A увімкнено (комплементарний) */
#define TIM_CCER_CH2_EN      (1U << 4)  /**< High-Side напівмоста B увімкнено */
#define TIM_CCER_CH2N_EN     (1U << 6)  /**< Low-Side напівмоста B увімкнено (комплементарний) */

/**
 * @brief Низькорівнева ініціалізація регістрів таймера та dead-time
 * @param period Період таймера ШІМ у відліках (частота зазвичай 15-25 кГц)
 * @param dead_time_counts Кількість тактів захисної паузи між перемиканнями ключів
 */
static void hw_timer_init(uint16_t period, uint16_t dead_time_counts)
{
    s_hw_tim.arr = (uint32_t)period;
    /* Програмування апаратного вузла Dead-Time Generator (DTG) */
    s_hw_tim.bdtr = (uint32_t)dead_time_counts;
    s_hw_tim.ccr1 = 0;
    s_hw_tim.ccr2 = 0;
    s_hw_tim.ccer = 0;
    s_hw_tim.cr1 = 1U; /* Запуск лічильника таймера */
}

/**
 * @brief Застосування конфігурації виходів таймера та шпаруватості до H-моста
 *
 * @param state Поточний режим моста (STOP, FORWARD, REVERSE, BRAKE)
 * @param duty Активне значення шпаруватості (0 .. arr)
 */
static void hw_timer_apply(motor_state_t state, uint16_t duty)
{
    switch (state) {
    case MOTOR_STATE_FORWARD:
        /*
         * Прямий рух:
         * Напівміст A комутується ШІМ-сигналом з активним dead-time (CH1/CH1N).
         * Напівміст B постійно притягнутий до GND (Low-Side ключ відкритий: CH2N=1, CH2=0).
         */
        s_hw_tim.ccr1 = (uint32_t)duty;
        s_hw_tim.ccr2 = 0;
        s_hw_tim.ccer = TIM_CCER_CH1_EN | TIM_CCER_CH1N_EN | TIM_CCER_CH2N_EN;
        break;

    case MOTOR_STATE_REVERSE:
        /*
         * Зворотний рух:
         * Напівміст B комутується ШІМ-сигналом з активним dead-time (CH2/CH2N).
         * Напівміст A постійно притягнутий до GND (Low-Side ключ відкритий: CH1N=1, CH1=0).
         */
        s_hw_tim.ccr1 = 0;
        s_hw_tim.ccr2 = (uint32_t)duty;
        s_hw_tim.ccer = TIM_CCER_CH2_EN | TIM_CCER_CH2N_EN | TIM_CCER_CH1N_EN;
        break;

    case MOTOR_STATE_BRAKE:
        /*
         * Активне динамічне гальмування (low-side clamp):
         * Обидва верхні ключі вимкнено (CH1=0, CH2=0).
         * Обидва нижні ключі увімкнено (CH1N=1, CH2N=1), що коротить клеми мотора на GND.
         * Проти-ЕРС генерує зворотний струм, який швидко гасить кінетичну енергію ротора.
         */
        s_hw_tim.ccr1 = 0;
        s_hw_tim.ccr2 = 0;
        s_hw_tim.ccer = TIM_CCER_CH1N_EN | TIM_CCER_CH2N_EN;
        break;

    case MOTOR_STATE_STOP:
    default:
        /*
         * Вільний вибіг (coasting):
         * Усі ключі розімкнено (стан високого імпедансу Hi-Z, виходи вимкнені).
         * Струм обмотки затухає через зворотні діоди, двигун долає лише власне тертя.
         */
        s_hw_tim.ccr1 = 0;
        s_hw_tim.ccr2 = 0;
        s_hw_tim.ccer = 0;
        break;
    }
}

/*
 * ============================================================================
 * ПУБЛІЧНИЙ ІНТЕРФЕЙС ДРАЙВЕРА МОТОР-РЕДУКТОРА
 * ============================================================================
 */

bool gearmotor_init(gearmotor_t *motor, const gearmotor_config_t *config)
{
    if (motor == NULL || config == NULL) {
        return false;
    }
    if (config->pwm_period == 0 || config->ramp_step == 0) {
        return false;
    }

    motor->pwm_period = config->pwm_period;
    motor->dead_time_counts = config->dead_time_counts;
    motor->ramp_step = config->ramp_step;
    motor->deadband_ticks = config->deadband_ticks;

    motor->current_duty = 0;
    motor->target_duty = 0;
    motor->state = MOTOR_STATE_STOP;
    motor->target_dir = MOTOR_DIR_FORWARD;
    motor->deadband_counter = 0;

    hw_timer_init(motor->pwm_period, motor->dead_time_counts);
    hw_timer_apply(MOTOR_STATE_STOP, 0);

    return true;
}

void gearmotor_set_speed(gearmotor_t *motor, uint16_t duty)
{
    if (motor == NULL) {
        return;
    }

    /* Насичення шпаруватості максимальним значенням періоду таймера */
    if (duty > motor->pwm_period) {
        duty = motor->pwm_period;
    }

    motor->target_duty = duty;

    /*
     * Якщо мотор перебував у режимі активного гальмування або повної зупинки
     * і подано команду на рух, переводимо його в готовність до старту.
     */
    if (motor->state == MOTOR_STATE_BRAKE && duty > 0) {
        motor->state = MOTOR_STATE_STOP;
    }
}

void gearmotor_set_direction(gearmotor_t *motor, motor_dir_t dir)
{
    if (motor == NULL) {
        return;
    }

    if (motor->target_dir == dir) {
        return;
    }

    motor->target_dir = dir;

    /*
     * БЕЗПЕКА РЕВЕРСУ:
     * Ми навмисно НЕ змінюємо стан motor->state тут.
     * Якщо ротор обертається, миттєве перемикання полярності викликає протиувімкнення:
     * напруга мережі 6 В додається до проти-ЕРС, викликаючи піковий струм у 2-3 рази
     * вищий за пусковий (I_plug > 3 А). Це спричиняє просідання живлення мікроконтролера
     * та миттєво зрізає пластикові чи латунні шестерні редуктора 100/600 об/хв.
     *
     * Неблокувальний автомат у gearmotor_update() розпізнає невідповідність напрямків,
     * лінійно зменшить швидкість до 0, витримає паузу мертвої зони (deadband),
     * і лише тоді безпечно почне розгін у новому напрямку.
     */
}

void gearmotor_update(gearmotor_t *motor)
{
    if (motor == NULL) {
        return;
    }

    switch (motor->state) {
    case MOTOR_STATE_BRAKE:
        /* У режимі активного гальмування шпаруватість нульова */
        motor->current_duty = 0;
        hw_timer_apply(MOTOR_STATE_BRAKE, 0);
        break;

    case MOTOR_STATE_STOP:
        motor->current_duty = 0;

        /*
         * Якщо активний лічильник мертвої зони реверсу — витримуємо захисну паузу.
         * Це дає змогу ротору зупинитися механічно, а індуктивній енергії обмотки —
         * повністю розсіятися перед подачею напруги зворотної полярності.
         */
        if (motor->deadband_counter > 0) {
            motor->deadband_counter--;
            hw_timer_apply(MOTOR_STATE_STOP, 0);
            break;
        }

        /* Якщо задано рух — переходимо у відповідний стан та починаємо плавний пуск */
        if (motor->target_duty > 0) {
            motor->state = (motor->target_dir == MOTOR_DIR_FORWARD)
                           ? MOTOR_STATE_FORWARD
                           : MOTOR_STATE_REVERSE;

            /* Початковий крок наростання шпаруватості (софт-старт) */
            if (motor->ramp_step >= motor->target_duty) {
                motor->current_duty = motor->target_duty;
            } else {
                motor->current_duty = motor->ramp_step;
            }
        }

        hw_timer_apply(motor->state, motor->current_duty);
        break;

    case MOTOR_STATE_FORWARD:
        /* Перевірка: чи не задано реверс напрямку? */
        if (motor->target_dir != MOTOR_DIR_FORWARD) {
            /*
             * Запит на зміну напрямку: спочатку лінійно сповільнюємось до нуля.
             * Обмежуємо темп спадання кроком ramp_step.
             */
            if (motor->current_duty > motor->ramp_step) {
                motor->current_duty -= motor->ramp_step;
            } else {
                /* Швидкість досягла нуля: входимо в стан STOP і запускаємо мертву зону */
                motor->current_duty = 0;
                motor->state = MOTOR_STATE_STOP;
                motor->deadband_counter = motor->deadband_ticks;
            }
        } else {
            /* Рух уперед: регулювання темпу розгону або сповільнення до target_duty */
            if (motor->current_duty < motor->target_duty) {
                /* Софт-старт: плавне лінійне збільшення шпаруватості (обмеження dI/dt) */
                if ((uint32_t)motor->current_duty + motor->ramp_step >= motor->target_duty) {
                    motor->current_duty = motor->target_duty;
                } else {
                    motor->current_duty += motor->ramp_step;
                }
            } else if (motor->current_duty > motor->target_duty) {
                /* Кероване лінійне сповільнення */
                if (motor->current_duty - motor->target_duty <= motor->ramp_step) {
                    motor->current_duty = motor->target_duty;
                } else {
                    motor->current_duty -= motor->ramp_step;
                }
            }

            /* Якщо цільова швидкість 0 і розгінний процес завершено — зупинка */
            if (motor->current_duty == 0 && motor->target_duty == 0) {
                motor->state = MOTOR_STATE_STOP;
            }
        }

        hw_timer_apply(motor->state, motor->current_duty);
        break;

    case MOTOR_STATE_REVERSE:
        /* Перевірка: чи не задано реверс напрямку? */
        if (motor->target_dir != MOTOR_DIR_REVERSE) {
            /* Лінійне уповільнення до повної зупинки */
            if (motor->current_duty > motor->ramp_step) {
                motor->current_duty -= motor->ramp_step;
            } else {
                motor->current_duty = 0;
                motor->state = MOTOR_STATE_STOP;
                motor->deadband_counter = motor->deadband_ticks;
            }
        } else {
            /* Реверсивний рух: регулювання шпаруватості */
            if (motor->current_duty < motor->target_duty) {
                /* Софт-старт у зворотному напрямку */
                if ((uint32_t)motor->current_duty + motor->ramp_step >= motor->target_duty) {
                    motor->current_duty = motor->target_duty;
                } else {
                    motor->current_duty += motor->ramp_step;
                }
            } else if (motor->current_duty > motor->target_duty) {
                /* Плавне уповільнення */
                if (motor->current_duty - motor->target_duty <= motor->ramp_step) {
                    motor->current_duty = motor->target_duty;
                } else {
                    motor->current_duty -= motor->ramp_step;
                }
            }

            if (motor->current_duty == 0 && motor->target_duty == 0) {
                motor->state = MOTOR_STATE_STOP;
            }
        }

        hw_timer_apply(motor->state, motor->current_duty);
        break;

    default:
        gearmotor_stop(motor);
        break;
    }
}

void gearmotor_stop(gearmotor_t *motor)
{
    if (motor == NULL) {
        return;
    }

    motor->state = MOTOR_STATE_STOP;
    motor->current_duty = 0;
    motor->target_duty = 0;
    motor->deadband_counter = 0;

    hw_timer_apply(MOTOR_STATE_STOP, 0);
}

void gearmotor_brake(gearmotor_t *motor)
{
    if (motor == NULL) {
        return;
    }

    motor->state = MOTOR_STATE_BRAKE;
    motor->current_duty = 0;
    motor->target_duty = 0;
    motor->deadband_counter = 0;

    hw_timer_apply(MOTOR_STATE_BRAKE, 0);
}

motor_state_t gearmotor_get_state(const gearmotor_t *motor)
{
    return (motor != NULL) ? motor->state : MOTOR_STATE_STOP;
}

uint16_t gearmotor_get_current_duty(const gearmotor_t *motor)
{
    return (motor != NULL) ? motor->current_duty : 0;
}

bool gearmotor_is_ramp_complete(const gearmotor_t *motor)
{
    if (motor == NULL) {
        return true;
    }

    if (motor->state == MOTOR_STATE_STOP) {
        return (motor->deadband_counter == 0) &&
               (motor->target_duty == 0) &&
               (motor->current_duty == 0);
    }

    if (motor->state == MOTOR_STATE_BRAKE) {
        return (motor->target_duty == 0);
    }

    if (motor->state == MOTOR_STATE_FORWARD) {
        return (motor->target_dir == MOTOR_DIR_FORWARD) &&
               (motor->current_duty == motor->target_duty);
    }

    if (motor->state == MOTOR_STATE_REVERSE) {
        return (motor->target_dir == MOTOR_DIR_REVERSE) &&
               (motor->current_duty == motor->target_duty);
    }

    return true;
}
