#include <stdint.h>
#include <stdbool.h>

/* Структура конфігурації та стану силового ШІМ-каналу */
typedef struct {
    uint8_t  gpio_pin;
    uint16_t current_duty;    /* 0 .. 1000 (0.0% .. 100.0%) */
    uint16_t target_duty;     /* Цільова шпаруватість */
    uint16_t step_ramp;       /* Крок зміни за один такт */
    bool     is_enabled;
} PwmPowerChannel;

/* Ініціалізація силового каналу */
void pwm_channel_init(PwmPowerChannel *chan, uint8_t pin, uint16_t ramp_step) {
    chan->gpio_pin = pin;
    chan->current_duty = 0;
    chan->target_duty = 0;
    chan->step_ramp = ramp_step;
    chan->is_enabled = false;
    /* Платформозалежна ініціалізація таймера: частота 1 кГц, вихід у 0 В */
}

/* Встановлення цільової яскравості / потужності з плавним переходом */
void pwm_channel_set_target(PwmPowerChannel *chan, uint16_t target) {
    if (target > 1000) {
        target = 1000;
    }
    chan->target_duty = target;
    chan->is_enabled = (target > 0);
}

/* Аварійне миттєве вимкнення (захист при КЗ чи перегріві) */
void pwm_channel_emergency_stop(PwmPowerChannel *chan) {
    chan->target_duty = 0;
    chan->current_duty = 0;
    chan->is_enabled = false;
    /* Апаратно скидаємо вихід таймера в низький рівень */
}

/* Періодичний обробник рампи плавного пуску (викликається кожні 10 мс) */
void pwm_channel_update_tick(PwmPowerChannel *chan) {
    if (chan->current_duty < chan->target_duty) {
        if (chan->current_duty + chan->step_ramp >= chan->target_duty) {
            chan->current_duty = chan->target_duty;
        } else {
            chan->current_duty += chan->step_ramp;
        }
    } else if (chan->current_duty > chan->target_duty) {
        if (chan->current_duty <= chan->step_ramp || 
            chan->current_duty - chan->step_ramp <= chan->target_duty) {
            chan->current_duty = chan->target_duty;
        } else {
            chan->current_duty -= chan->step_ramp;
        }
    }
    /* Запис нового значення current_duty у регістр порівняння таймера */
}
