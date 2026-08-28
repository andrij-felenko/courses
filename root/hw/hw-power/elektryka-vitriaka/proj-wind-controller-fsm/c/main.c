#include <stdint.h>
#include <stdbool.h>

/* Пороги напруги в мілівольтах (мВ) */
#define VBAT_NOMINAL_MV          48000U
#define VBAT_FLOAT_TARGET_MV     54400U  /* Напруга підтримувального заряду */
#define VBAT_ABSORPTION_MAX_MV   57600U  /* Верхня межа заряду */
#define VBAT_OVERVOLTAGE_ALARM_MV 60000U /* Аварійний поріг відсічки */

/* Механічні пороги обертів ротора (об/хв) */
#define RPM_CUT_IN                 120U  /* Оберти початку заряду */
#define RPM_RATED                  450U  /* Номінальні оберти */
#define RPM_OVERSPEED_LIMIT        550U  /* Поріг штормової аварії */
#define RPM_SAFE_BRAKE             200U  /* Безпечні оберти для замикання реле */

/* Часові константи (мілісекунди) */
#define MPPT_UPDATE_INTERVAL_MS    100UL /* Крок адаптації згладженого MPPT */
#define BRAKE_DUMP_TIMEOUT_MS     5000UL /* Максимальний час здуття обертів баластом */

typedef enum {
    WIND_STATE_PARKED_BRAKED = 0,
    WIND_STATE_STARTUP_RELEASE,
    WIND_STATE_MPPT_TRACKING,
    WIND_STATE_POWER_LIMIT_DUMP,
    WIND_STATE_HIGH_WIND_BRAKING,
    WIND_STATE_FAULT_LATCH
} wind_state_t;

typedef enum {
    WIND_FAULT_NONE = 0,
    WIND_FAULT_BATTERY_OVERVOLTAGE,
    WIND_FAULT_ROTOR_OVERSPEED,
    WIND_FAULT_HEATSINK_OVERTEMP
} wind_fault_t;

typedef struct {
    wind_state_t state;
    wind_fault_t fault;
    uint32_t state_entry_time_ms;
    uint32_t last_mppt_tick_ms;
    uint16_t rpm_filtered;
    uint16_t vbat_mv;
    uint16_t vgen_mv;
    uint16_t igen_ma;
    uint16_t mppt_pwm_permille;  /* ШІМ MPPT (0..1000) */
    uint16_t dump_pwm_permille;  /* ШІМ баласту (0..1000) */
    bool brake_relay_closed;
} wind_controller_t;

/* Апаратні функції драйверів (HAL) */
extern void hw_set_mppt_pwm(uint16_t permille);
extern void hw_set_dump_pwm(uint16_t permille);
extern void hw_set_brake_relay(bool close_short_circuit);
extern uint32_t hw_get_time_ms(void);

void wind_controller_init(wind_controller_t *ctrl)
{
    if (!ctrl) return;
    ctrl->state = WIND_STATE_PARKED_BRAKED;
    ctrl->fault = WIND_FAULT_NONE;
    ctrl->state_entry_time_ms = hw_get_time_ms();
    ctrl->last_mppt_tick_ms = ctrl->state_entry_time_ms;
    ctrl->rpm_filtered = 0;
    ctrl->vbat_mv = 0;
    ctrl->vgen_mv = 0;
    ctrl->igen_ma = 0;
    ctrl->mppt_pwm_permille = 0;
    ctrl->dump_pwm_permille = 0;
    ctrl->brake_relay_closed = true;

    /* За замовчуванням генератор надійно закорочений */
    hw_set_mppt_pwm(0);
    hw_set_dump_pwm(0);
    hw_set_brake_relay(true);
}

static void wind_transition_to(wind_controller_t *ctrl, wind_state_t new_state)
{
    ctrl->state = new_state;
    ctrl->state_entry_time_ms = hw_get_time_ms();

    switch (new_state) {
    case WIND_STATE_PARKED_BRAKED:
    case WIND_STATE_FAULT_LATCH:
        hw_set_mppt_pwm(0);
        hw_set_dump_pwm(1000); /* Баласт паралельно реле */
        hw_set_brake_relay(true);
        ctrl->brake_relay_closed = true;
        ctrl->mppt_pwm_permille = 0;
        ctrl->dump_pwm_permille = 1000;
        break;

    case WIND_STATE_STARTUP_RELEASE:
        hw_set_brake_relay(false);
        hw_set_mppt_pwm(0);
        hw_set_dump_pwm(0);
        ctrl->brake_relay_closed = false;
        ctrl->mppt_pwm_permille = 0;
        ctrl->dump_pwm_permille = 0;
        break;

    case WIND_STATE_MPPT_TRACKING:
        hw_set_brake_relay(false);
        hw_set_dump_pwm(0);
        ctrl->brake_relay_closed = false;
        ctrl->dump_pwm_permille = 0;
        break;

    case WIND_STATE_POWER_LIMIT_DUMP:
        hw_set_brake_relay(false);
        ctrl->brake_relay_closed = false;
        break;

    case WIND_STATE_HIGH_WIND_BRAKING:
        /* Спочатку 100% баласт для здуття швидкості, реле ще не замикаємо */
        hw_set_mppt_pwm(0);
        hw_set_dump_pwm(1000);
        hw_set_brake_relay(false);
        ctrl->brake_relay_closed = false;
        ctrl->mppt_pwm_permille = 0;
        ctrl->dump_pwm_permille = 1000;
        break;
    }
}

/* Обчислення цільової потужності за кубічною характеристикою P_opt = k * w^3 */
static uint16_t calculate_optimal_mppt_pwm(uint16_t rpm, uint16_t vgen_mv)
{
    if (rpm < RPM_CUT_IN || vgen_mv < 10000U) return 0;
    
    /* Спрощена кубічна апроксимація шпаруватості від обертів */
    uint32_t norm_rpm = (uint32_t)(rpm - RPM_CUT_IN);
    uint32_t max_span = (uint32_t)(RPM_RATED - RPM_CUT_IN);
    if (norm_rpm > max_span) norm_rpm = max_span;

    uint32_t target = (norm_rpm * norm_rpm * norm_rpm) / (max_span * max_span / 1000U);
    if (target > 1000U) target = 1000U;
    return (uint16_t)target;
}

void wind_controller_process(wind_controller_t *ctrl,
                             uint16_t raw_rpm,
                             uint16_t raw_vbat_mv,
                             uint16_t raw_vgen_mv,
                             uint16_t raw_igen_ma,
                             bool temp_ok)
{
    uint32_t now = hw_get_time_ms();

    /* Фільтрація вимірювань ковзним середнім (експоненційний IIR) */
    ctrl->rpm_filtered = (uint16_t)(((uint32_t)ctrl->rpm_filtered * 3U + raw_rpm) / 4U);
    ctrl->vbat_mv      = (uint16_t)(((uint32_t)ctrl->vbat_mv * 3U + raw_vbat_mv) / 4U);
    ctrl->vgen_mv      = (uint16_t)(((uint32_t)ctrl->vgen_mv * 3U + raw_vgen_mv) / 4U);
    ctrl->igen_ma      = raw_igen_ma;

    /* Глобальні аварійні перевірки */
    if (!temp_ok) {
        ctrl->fault = WIND_FAULT_HEATSINK_OVERTEMP;
        wind_transition_to(ctrl, WIND_STATE_FAULT_LATCH);
        return;
    }
    if (ctrl->vbat_mv > VBAT_OVERVOLTAGE_ALARM_MV) {
        ctrl->fault = WIND_FAULT_BATTERY_OVERVOLTAGE;
        wind_transition_to(ctrl, WIND_STATE_FAULT_LATCH);
        return;
    }
    if (ctrl->rpm_filtered > RPM_OVERSPEED_LIMIT && ctrl->state != WIND_STATE_HIGH_WIND_BRAKING) {
        ctrl->fault = WIND_FAULT_ROTOR_OVERSPEED;
        wind_transition_to(ctrl, WIND_STATE_HIGH_WIND_BRAKING);
        return;
    }

    switch (ctrl->state) {
    case WIND_STATE_PARKED_BRAKED:
        /* Вихід із паркування за командою оператора або після перезапуску */
        break;

    case WIND_STATE_STARTUP_RELEASE:
        if (ctrl->rpm_filtered >= RPM_CUT_IN) {
            wind_transition_to(ctrl, WIND_STATE_MPPT_TRACKING);
        }
        break;

    case WIND_STATE_MPPT_TRACKING:
        if (ctrl->rpm_filtered < (RPM_CUT_IN - 20U)) {
            wind_transition_to(ctrl, WIND_STATE_STARTUP_RELEASE);
            break;
        }

        /* Перехід у захист баластом при наборі повної ємності АКБ */
        if (ctrl->vbat_mv >= VBAT_FLOAT_TARGET_MV || ctrl->rpm_filtered >= RPM_RATED) {
            wind_transition_to(ctrl, WIND_STATE_POWER_LIMIT_DUMP);
            break;
        }

        /* Періодичне оновлення MPPT */
        if ((now - ctrl->last_mppt_tick_ms) >= MPPT_UPDATE_INTERVAL_MS) {
            ctrl->last_mppt_tick_ms = now;
            ctrl->mppt_pwm_permille = calculate_optimal_mppt_pwm(ctrl->rpm_filtered, ctrl->vgen_mv);
            hw_set_mppt_pwm(ctrl->mppt_pwm_permille);
        }
        break;

    case WIND_STATE_POWER_LIMIT_DUMP:
        /* П-регулятор баласту для утримання цільової напруги */
        if (ctrl->vbat_mv > VBAT_FLOAT_TARGET_MV) {
            uint32_t err = (uint32_t)(ctrl->vbat_mv - VBAT_FLOAT_TARGET_MV);
            uint32_t duty = (err * 1000U) / (VBAT_ABSORPTION_MAX_MV - VBAT_FLOAT_TARGET_MV);
            if (duty > 1000U) duty = 1000U;
            ctrl->dump_pwm_permille = (uint16_t)duty;
        } else {
            ctrl->dump_pwm_permille = 0;
            if (ctrl->rpm_filtered < (RPM_RATED - 30U)) {
                wind_transition_to(ctrl, WIND_STATE_MPPT_TRACKING);
            }
        }
        hw_set_dump_pwm(ctrl->dump_pwm_permille);
        break;

    case WIND_STATE_HIGH_WIND_BRAKING:
        /* Очікування зниження обертів баластом перед фіксацією реле */
        if (ctrl->rpm_filtered <= RPM_SAFE_BRAKE || (now - ctrl->state_entry_time_ms) > BRAKE_DUMP_TIMEOUT_MS) {
            hw_set_brake_relay(true);
            ctrl->brake_relay_closed = true;
            wind_transition_to(ctrl, WIND_STATE_PARKED_BRAKED);
        }
        break;

    case WIND_STATE_FAULT_LATCH:
        /* Блокування до зняття живлення або очищення помилки */
        break;
    }
}
