#include "safe_actuator.h"

#include "hw.h"

/* Результат одного опитування рубежів безпеки. */
typedef struct {
    uint16_t voltage_mv;
    bool     overtemp;
    bool     overcurrent;
    bool     ok;
} safety_limits_t;

/* --- внутрішні помічники ------------------------------------------------ */

static void enter_fault(safe_actuator_t *drv, actuator_fault_t reason)
{
    /* Перша причина — головна. Наступні аварії її не перезаписують:
     * діагностика має показати, що зламалося першим. */
    if (drv->fault == FAULT_NONE) {
        drv->fault = reason;
    }
    drv->state = ACTUATOR_FAULT;
    drv->current_pwm = 0;
    drv->hb_phase = false;
}

static void checkpoint(safe_actuator_t *drv, actuator_checkpoint_t chk)
{
    /* Чекпойнт зараховується, лише коли всі попередні вже пройдено:
     * порядок опитування — така сама частина протоколу, як і сам факт. */
    uint8_t required = (uint8_t)((uint8_t)chk - 1U);
    if (drv->checkpoints == required) {
        drv->checkpoints |= (uint8_t)chk;
    }
}

static safety_limits_t read_limits(void)
{
    safety_limits_t lim;
    lim.voltage_mv  = hw_read_supply_voltage_mv();
    lim.overtemp    = hw_read_overtemp_flag();
    lim.overcurrent = hw_read_overcurrent_flag();
    lim.ok = (lim.voltage_mv >= MIN_SAFE_VOLTAGE_MV) &&
             (lim.voltage_mv <= MAX_SAFE_VOLTAGE_MV) &&
             !lim.overtemp && !lim.overcurrent;
    return lim;
}

static actuator_fault_t limits_fault(const safety_limits_t *lim)
{
    if (lim->overcurrent) {
        return FAULT_OVERCURRENT;
    }
    if (lim->overtemp) {
        return FAULT_OVERTEMP;
    }
    return FAULT_VOLTAGE;
}

/* Меандр 1 кГц. Фаза перемикається за часом, а не за кількістю викликів:
 * прив'язка до тактів циклу зробила б частоту помпи заручником джитера. */
static void drive_heartbeat(safe_actuator_t *drv, uint32_t now_us)
{
    uint32_t elapsed = now_us - drv->hb_last_toggle_us;

    if (elapsed >= HEARTBEAT_STALL_US) {
        /* Цикл спізнився настільки, що фільтр помпи вже просів. Далі
         * генерувати меандр немає сенсу — ключ і так розімкнувся. */
        enter_fault(drv, FAULT_HEARTBEAT_STALL);
        return;
    }

    if (elapsed >= HEARTBEAT_HALF_PERIOD_US) {
        drv->hb_phase = !drv->hb_phase;
        drv->hb_last_toggle_us = now_us;
    }
}

/* Єдине місце в драйвері, що торкається виходів. */
static void apply_outputs(const safe_actuator_t *drv)
{
    if (drv->state == ACTUATOR_ARMED) {
        hw_gpio_write_heartbeat(drv->hb_phase);
        hw_timer_set_pwm_duty(drv->current_pwm);
    } else {
        /* Спершу знімаємо силу, і тільки потім — дозвіл. Зворотний порядок
         * лишив би вікно, у якому ШІМ ще котиться на живому ключі. */
        hw_timer_set_pwm_duty(0);
        hw_gpio_write_heartbeat(false);
    }
}

/* --- публічний інтерфейс ------------------------------------------------ */

void safe_actuator_init(safe_actuator_t *drv)
{
    /* Виходи в безпечний нуль до будь-якої іншої дії. */
    hw_timer_set_pwm_duty(0);
    hw_gpio_write_heartbeat(false);

    drv->state = ACTUATOR_DISARMED;
    drv->fault = FAULT_NONE;
    drv->arm_request_us = 0;
    drv->hb_last_toggle_us = 0;
    drv->current_pwm = 0;
    drv->checkpoints = 0;
    drv->hb_phase = false;
}

bool safe_actuator_request_arm(safe_actuator_t *drv, uint32_t token)
{
    if (token != SAFE_ARM_TOKEN) {
        enter_fault(drv, FAULT_BAD_TOKEN);
        apply_outputs(drv);
        return false;
    }

    if (drv->state != ACTUATOR_DISARMED) {
        /* Повторний запит із ARMED чи FAULT — ознака того, що логіка місії
         * загубила стан. Такому виклику не можна просто відмовити. */
        enter_fault(drv, FAULT_SEQUENCE);
        apply_outputs(drv);
        return false;
    }

    drv->state = ACTUATOR_ARM_REQUESTED;
    drv->arm_request_us = hw_get_time_us();
    return true;
}

void safe_actuator_disarm(safe_actuator_t *drv)
{
    drv->current_pwm = 0;
    drv->hb_phase = false;

    if (drv->state != ACTUATOR_FAULT) {
        drv->state = ACTUATOR_DISARMED;
    }

    /* Виходи гасимо тут-таки, не чекаючи наступного циклу. */
    hw_timer_set_pwm_duty(0);
    hw_gpio_write_heartbeat(false);
}

void safe_actuator_process_cycle(safe_actuator_t *drv, uint16_t target_pwm)
{
    const uint32_t now_us = hw_get_time_us();
    safety_limits_t lim;

    drv->checkpoints = 0;

    /* Рубіж 1. Аварійна зупинка. Фільтра деренчання на небезпечному напрямку
     * немає навмисно: активний рівень діє з першого ж зчитування. Затримка
     * тут — це затримка зняття сили, а вона нікого не рятує. */
    if (hw_read_estop_active()) {
        enter_fault(drv, FAULT_ESTOP);
    }
    checkpoint(drv, CHK_ESTOP);

    /* Рубіж 2. Межі живлення й силового каскаду. Опитуємо їх щоцикла, а не
     * лише перед узяттям під силу: батарея просідає саме під навантаженням. */
    lim = read_limits();
    checkpoint(drv, CHK_LIMITS);

    /* Рубіж 3. Автомат станів. */
    switch (drv->state) {
    case ACTUATOR_DISARMED:
        drv->current_pwm = 0;
        drv->hb_phase = false;
        break;

    case ACTUATOR_ARM_REQUESTED:
        if ((now_us - drv->arm_request_us) > ARM_SEQUENCE_TIMEOUT_US) {
            enter_fault(drv, FAULT_ARM_TIMEOUT);
        } else {
            drv->state = ACTUATOR_PRE_ARM_CHECK;
        }
        break;

    case ACTUATOR_PRE_ARM_CHECK:
        if ((now_us - drv->arm_request_us) > ARM_SEQUENCE_TIMEOUT_US) {
            enter_fault(drv, FAULT_ARM_TIMEOUT);
        } else if (!lim.ok) {
            enter_fault(drv, limits_fault(&lim));
        } else {
            drv->state = ACTUATOR_ARMED;
            drv->current_pwm = 0;
            /* Меандр стартує з нульової фази, а ШІМ — з нуля: сила
             * з'являється на ключі раніше, ніж на моторі. */
            drv->hb_phase = false;
            drv->hb_last_toggle_us = now_us;
        }
        break;

    case ACTUATOR_ARMED:
        if (!lim.ok) {
            enter_fault(drv, limits_fault(&lim));
            break;
        }
        drive_heartbeat(drv, now_us);
        if (drv->state != ACTUATOR_ARMED) {
            break; /* серцебиття зірвалося, стан уже FAULT */
        }
        drv->current_pwm = (target_pwm > PWM_MAX_DUTY) ? PWM_MAX_DUTY
                                                       : target_pwm;
        break;

    case ACTUATOR_FAULT:
    default:
        /* Виходу з аварії немає: лише повний перезапуск мікроконтролера. */
        enter_fault(drv, FAULT_SEQUENCE);
        break;
    }
    checkpoint(drv, CHK_STATE);

    /* Рубіж 4. Виходи. */
    apply_outputs(drv);
    checkpoint(drv, CHK_OUTPUT);

    /* Сторож дізнається про життя лише в кінці повного циклу валідації.
     * Аварійний стан цикл теж проходить цілком — інакше сторож скинув би
     * контролер і стер причину аварії раніше, ніж її встигли прочитати. */
    if (drv->checkpoints == CHK_ALL) {
        hw_watchdog_feed();
    }
}
