/* corona_driver.c — Реалізація драйвера високовольтної корони мовою C */

#include <stdint.h>
#include <stdbool.h>

#define PWM_MAX_DUTY        1024U
#define CORONA_SETPOINT_UA  200U   /* Цільовий струм корони: 200 мкА */
#define TRIP_CURRENT_UA     1500U  /* Поріг аварійного обриву дуги: 1.5 мА */
#define RECOVERY_DELAY_MS   50U

typedef enum {
    CORONA_STATE_OFF = 0,
    CORONA_STATE_SOFT_START,
    CORONA_STATE_RUNNING,
    CORONA_STATE_ARC_TRIPPED
} corona_state_t;

typedef struct {
    corona_state_t state;
    uint32_t current_ua;      /* Поточний виміряний струм (мкА) */
    uint32_t target_ua;       /* Уставка струму (мкА) */
    uint16_t pwm_duty;        /* Поточний ШІМ (0..1024) */
    uint32_t trip_count;      /* Лічильник спрацьовувань захисту */
    uint32_t recovery_timer;  /* Таймер відновлення */
    
    /* Коефіцієнти ПІД-регулятора */
    int32_t kp;
    int32_t ki;
    int32_t integral;
} corona_driver_t;

/* Глобальний екземпляр драйвера */
static corona_driver_t g_corona;

/* Апаратні функції-заглушки для виклику периферії MCU */
static inline void hardware_pwm_set_duty(uint16_t duty) {
    /* Запис у регістр порівняння таймера ШІМ (наприклад, TIM1->CCR1) */
    (void)duty;
}

static inline void hardware_pwm_disable(void) {
    /* Негайне аварійне вимкнення виходу ШІМ */
    hardware_pwm_set_duty(0);
}

static inline uint32_t hardware_adc_read_current_ua(void) {
    /* Зчитування АЦП із падіння напруги на шунті R_sense */
    /* 1 В на шунті 1 кОм відповідає 1000 мкА */
    return g_corona.current_ua; /* У симуляції повертаємо поточний струм */
}

void corona_init(corona_driver_t *drv, uint32_t target_ua) {
    drv->state = CORONA_STATE_OFF;
    drv->current_ua = 0;
    drv->target_ua = target_ua;
    drv->pwm_duty = 0;
    drv->trip_count = 0;
    drv->recovery_timer = 0;
    drv->kp = 2;
    drv->ki = 1;
    drv->integral = 0;
    hardware_pwm_disable();
}

void corona_start(corona_driver_t *drv) {
    drv->state = CORONA_STATE_SOFT_START;
    drv->pwm_duty = 50; /* Початковий мінімальний ШІМ */
    drv->integral = 0;
    hardware_pwm_set_duty(drv->pwm_duty);
}

/* Швидкий обробник вибірки АЦП (викликається у перериванні АЦП/Таймера, наприклад 10 кГц) */
void corona_fast_isr_loop(corona_driver_t *drv) {
    if (drv->state == CORONA_STATE_OFF) {
        return;
    }

    uint32_t i_meas = hardware_adc_read_current_ua();
    drv->current_ua = i_meas;

    /* КРИТИЧНИЙ ЗАХИСТ: Негайний детектор дугового пробою */
    if (i_meas >= TRIP_CURRENT_UA) {
        hardware_pwm_disable();
        drv->pwm_duty = 0;
        drv->state = CORONA_STATE_ARC_TRIPPED;
        drv->trip_count++;
        drv->recovery_timer = RECOVERY_DELAY_MS;
        return;
    }

    /* ПІД-регулювання струму у робочих режимах */
    if (drv->state == CORONA_STATE_RUNNING || drv->state == CORONA_STATE_SOFT_START) {
        int32_t error = (int32_t)drv->target_ua - (int32_t)i_meas;
        drv->integral += error;
        
        /* Анти-вінд-ап обмеження інтеграла */
        if (drv->integral > 5000) drv->integral = 5000;
        if (drv->integral < -5000) drv->integral = -5000;

        int32_t output = (drv->kp * error) + ((drv->ki * drv->integral) / 100);
        int32_t new_duty = (int32_t)drv->pwm_duty + (output / 10);

        if (new_duty > (int32_t)PWM_MAX_DUTY) new_duty = PWM_MAX_DUTY;
        if (new_duty < 0) new_duty = 0;

        drv->pwm_duty = (uint16_t)new_duty;
        hardware_pwm_set_duty(drv->pwm_duty);

        if (drv->state == CORONA_STATE_SOFT_START && i_meas >= (drv->target_ua * 8 / 10)) {
            drv->state = CORONA_STATE_RUNNING;
        }
    }
}

/* Фоновий системний такт (викликається кожні 1 мс) */
void corona_process_tick_1ms(corona_driver_t *drv) {
    if (drv->state == CORONA_STATE_ARC_TRIPPED) {
        if (drv->recovery_timer > 0) {
            drv->recovery_timer--;
        } else {
            /* Перезапуск після аварії */
            corona_start(drv);
        }
    }
}
