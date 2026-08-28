#include <stdint.h>
#include <stdbool.h>

/* Пороги напруги в мілівольтах (мВ) */
#define VBAT_SHORT_THRESH_MV    1500U  /* Нижче 1.5 В — краплинне пробудження */
#define VBAT_PRECHG_THRESH_MV   3000U  /* Поріг переходу в CC: 3.0 В */
#define VBAT_HYST_MV             100U  /* Гістерезис перемикання: 100 мВ */
#define VBAT_REG_TARGET_MV      4200U  /* Цільова напруга CV: 4.20 В */

/* Ліміти струму в міліамперах (мА) для батареї 2000 мА·год */
#define CURRENT_TRICKLE_MA        30U  /* 0.015C для пробудження */
#define CURRENT_PRECHARGE_MA     150U  /* 0.075C струм передзаряду */
#define CURRENT_FAST_CC_MA      1000U  /* 0.5C струм швидкого заряду */
#define CURRENT_TERM_MA          100U  /* C/20 поріг термінації */

/* Таймери безпеки в мілісекундах */
#define PRECHARGE_TIMEOUT_MS  (45UL * 60UL * 1000UL) /* 45 хвилин максимум */
#define DEBOUNCE_DELAY_MS        200UL               /* Час стабілізації вимірювань */

typedef enum {
    CHARGE_STATE_IDLE = 0,
    CHARGE_STATE_TRICKLE,
    CHARGE_STATE_PRECHARGE,
    CHARGE_STATE_CONSTANT_CURRENT,
    CHARGE_STATE_CONSTANT_VOLTAGE,
    CHARGE_STATE_TERMINATION,
    CHARGE_STATE_FAULT_LATCH
} charge_state_t;

typedef enum {
    FAULT_NONE = 0,
    FAULT_PRECHARGE_TIMEOUT,
    FAULT_OVERVOLTAGE,
    FAULT_OVERTEMPERATURE
} charge_fault_t;

typedef struct {
    charge_state_t state;
    charge_fault_t fault;
    uint32_t state_entry_time_ms;
    uint32_t last_tick_time_ms;
    uint16_t vbat_filtered_mv;
    uint16_t ibat_filtered_ma;
    bool vbus_present;
} charger_fsm_t;

/* Апаратні абстракції керування силовим каскадом */
extern void hw_set_charge_current_limit(uint16_t ma);
extern void hw_set_charge_voltage_limit(uint16_t mv);
extern void hw_enable_charging(bool enable);
extern uint32_t hw_get_system_time_ms(void);

void charger_fsm_init(charger_fsm_t *fsm)
{
    if (!fsm) return;
    fsm->state = CHARGE_STATE_IDLE;
    fsm->fault = FAULT_NONE;
    fsm->state_entry_time_ms = hw_get_system_time_ms();
    fsm->last_tick_time_ms = fsm->state_entry_time_ms;
    fsm->vbat_filtered_mv = 0;
    fsm->ibat_filtered_ma = 0;
    fsm->vbus_present = false;

    hw_enable_charging(false);
    hw_set_charge_current_limit(0);
}

static void charger_transition(charger_fsm_t *fsm, charge_state_t new_state)
{
    fsm->state = new_state;
    fsm->state_entry_time_ms = hw_get_system_time_ms();

    switch (new_state) {
    case CHARGE_STATE_IDLE:
        hw_enable_charging(false);
        hw_set_charge_current_limit(0);
        break;

    case CHARGE_STATE_TRICKLE:
        hw_set_charge_voltage_limit(VBAT_PRECHG_THRESH_MV);
        hw_set_charge_current_limit(CURRENT_TRICKLE_MA);
        hw_enable_charging(true);
        break;

    case CHARGE_STATE_PRECHARGE:
        hw_set_charge_voltage_limit(VBAT_PRECHG_THRESH_MV);
        hw_set_charge_current_limit(CURRENT_PRECHARGE_MA);
        hw_enable_charging(true);
        break;

    case CHARGE_STATE_CONSTANT_CURRENT:
        hw_set_charge_voltage_limit(VBAT_REG_TARGET_MV);
        hw_set_charge_current_limit(CURRENT_FAST_CC_MA);
        hw_enable_charging(true);
        break;

    case CHARGE_STATE_CONSTANT_VOLTAGE:
        /* Регулятор автоматично тримає напругу та знижує струм */
        hw_set_charge_voltage_limit(VBAT_REG_TARGET_MV);
        hw_set_charge_current_limit(CURRENT_FAST_CC_MA);
        hw_enable_charging(true);
        break;

    case CHARGE_STATE_TERMINATION:
    case CHARGE_STATE_FAULT_LATCH:
        hw_enable_charging(false);
        hw_set_charge_current_limit(0);
        break;
    }
}

void charger_fsm_process(charger_fsm_t *fsm, uint16_t vbat_raw_mv, uint16_t ibat_raw_ma, bool vbus_ok)
{
    uint32_t now_ms = hw_get_system_time_ms();
    fsm->last_tick_time_ms = now_ms;
    fsm->vbus_present = vbus_ok;

    /* Простий експоненційний фільтр шуму АЦП: alpha = 0.25 */
    fsm->vbat_filtered_mv = (uint16_t)(((uint32_t)fsm->vbat_filtered_mv * 3U + vbat_raw_mv) / 4U);
    fsm->ibat_filtered_ma = (uint16_t)(((uint32_t)fsm->ibat_filtered_ma * 3U + ibat_raw_ma) / 4U);

    /* Аварійне скидання при відключенні кабелю VBUS */
    if (!vbus_ok) {
        if (fsm->state != CHARGE_STATE_IDLE && fsm->state != CHARGE_STATE_FAULT_LATCH) {
            charger_transition(fsm, CHARGE_STATE_IDLE);
        }
        return;
    }

    uint32_t time_in_state_ms = now_ms - fsm->state_entry_time_ms;

    switch (fsm->state) {
    case CHARGE_STATE_IDLE:
        if (fsm->vbat_filtered_mv < VBAT_SHORT_THRESH_MV) {
            charger_transition(fsm, CHARGE_STATE_TRICKLE);
        } else if (fsm->vbat_filtered_mv < VBAT_PRECHG_THRESH_MV) {
            charger_transition(fsm, CHARGE_STATE_PRECHARGE);
        } else if (fsm->vbat_filtered_mv < (VBAT_REG_TARGET_MV - 50U)) {
            charger_transition(fsm, CHARGE_STATE_CONSTANT_CURRENT);
        }
        break;

    case CHARGE_STATE_TRICKLE:
        /* Якщо батарея набрала 1.5 В — переходимо до передзаряду */
        if (fsm->vbat_filtered_mv >= VBAT_SHORT_THRESH_MV) {
            charger_transition(fsm, CHARGE_STATE_PRECHARGE);
        }
        break;

    case CHARGE_STATE_PRECHARGE:
        /* Перевірка таймера безпеки: чи не зависла комірка */
        if (time_in_state_ms > PRECHARGE_TIMEOUT_MS) {
            fsm->fault = FAULT_PRECHARGE_TIMEOUT;
            charger_transition(fsm, CHARGE_STATE_FAULT_LATCH);
            return;
        }

        /* Перехід у фазу CC з урахуванням гістерезису для захисту від брязкоту */
        if (fsm->vbat_filtered_mv >= (VBAT_PRECHG_THRESH_MV + VBAT_HYST_MV)) {
            charger_transition(fsm, CHARGE_STATE_CONSTANT_CURRENT);
        }
        break;

    case CHARGE_STATE_CONSTANT_CURRENT:
        /* Захисний відкат у передзаряд при раптовому просіданні напруги */
        if (fsm->vbat_filtered_mv < (VBAT_PRECHG_THRESH_MV - VBAT_HYST_MV)) {
            charger_transition(fsm, CHARGE_STATE_PRECHARGE);
            return;
        }

        /* Досягнення напруги стабілізації CV */
        if (fsm->vbat_filtered_mv >= VBAT_REG_TARGET_MV) {
            charger_transition(fsm, CHARGE_STATE_CONSTANT_VOLTAGE);
        }
        break;

    case CHARGE_STATE_CONSTANT_VOLTAGE:
        /* Термінація заряду за спаданням струму */
        if (fsm->ibat_filtered_ma < CURRENT_TERM_MA && time_in_state_ms > DEBOUNCE_DELAY_MS) {
            charger_transition(fsm, CHARGE_STATE_TERMINATION);
        }
        break;

    case CHARGE_STATE_TERMINATION:
        /* Автоматичний перезапуск заряду при саморозряді нижче 4.05 В */
        if (fsm->vbat_filtered_mv < (VBAT_REG_TARGET_MV - 150U)) {
            charger_transition(fsm, CHARGE_STATE_CONSTANT_CURRENT);
        }
        break;

    case CHARGE_STATE_FAULT_LATCH:
        /* Вихід лише через фізичне відключення та повторне підключення VBUS */
        break;
    }
}
