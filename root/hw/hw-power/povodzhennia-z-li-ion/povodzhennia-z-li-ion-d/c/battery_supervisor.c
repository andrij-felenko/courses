/* battery_supervisor.h / battery_supervisor.c */
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    BATT_STATE_SAFE_DISCHARGE = 0,
    BATT_STATE_JEITA_CHARGE,
    BATT_STATE_STORAGE_IDLE,
    BATT_STATE_FAULT_LOCKOUT
} batt_state_t;

typedef struct {
    uint16_t cell_voltage_mv;   /* Напруга комірки, мВ */
    int16_t  pack_temp_c;       /* Температура, градуси Цельсія */
    int16_t  charge_current_ma; /* Зарядний струм, мА */
} batt_telemetry_t;

typedef struct {
    bool charge_allowed;        /* Прапорець дозволу заряду */
    uint16_t max_voltage_mv;    /* Гранична напруга відсічки */
    uint16_t max_current_ma;    /* Дозволений струм */
    uint8_t fault_flags;        /* Маска помилок */
} batt_control_t;

#define FAULT_OVERVOLTAGE   (1 << 0)
#define FAULT_UNDERVOLTAGE  (1 << 1)
#define FAULT_COLD_CHARGE   (1 << 2)
#define FAULT_OVERTEMP      (1 << 3)
#define FAULT_DEEP_DISCHG   (1 << 4)

void batt_supervisor_step(const batt_telemetry_t *telem, batt_control_t *ctrl) {
    ctrl->fault_flags = 0;

    /* 1. Перевірка критичного перерозряду (< 2.0 В) — розчинення міді */
    if (telem->cell_voltage_mv < 2000) {
        ctrl->fault_flags |= FAULT_DEEP_DISCHG;
        ctrl->charge_allowed = false;
        ctrl->max_current_ma = 0;
        return; /* Повне блокування: заряд суворо заборонено! */
    }

    /* 2. Перевірка граничних напруг */
    if (telem->cell_voltage_mv > 4250) {
        ctrl->fault_flags |= FAULT_OVERVOLTAGE;
    }

    /* 3. Оцінка температурного вікна JEITA для заряду */
    if (telem->pack_temp_c < 0) {
        /* Холод: заборона заряду через плакування літію */
        ctrl->fault_flags |= FAULT_COLD_CHARGE;
        ctrl->charge_allowed = false;
        ctrl->max_current_ma = 0;
        ctrl->max_voltage_mv = 4200;
    } else if (telem->pack_temp_c < 10) {
        /* Прохолодно: знижений струм 0.2C */
        ctrl->charge_allowed = true;
        ctrl->max_current_ma = 500;
        ctrl->max_voltage_mv = 4200;
    } else if (telem->pack_temp_c <= 45) {
        /* Стандартний безпечний режим */
        ctrl->charge_allowed = true;
        ctrl->max_current_ma = 2000;
        ctrl->max_voltage_mv = 4200;
    } else if (telem->pack_temp_c < 60) {
        /* Тепло: зниження напруги до 4.10 В для захисту катода */
        ctrl->charge_allowed = true;
        ctrl->max_current_ma = 1000;
        ctrl->max_voltage_mv = 4100;
    } else {
        /* Спека: небезпека теплового розгону */
        ctrl->fault_flags |= FAULT_OVERTEMP;
        ctrl->charge_allowed = false;
        ctrl->max_current_ma = 0;
        ctrl->max_voltage_mv = 4100;
    }
}
