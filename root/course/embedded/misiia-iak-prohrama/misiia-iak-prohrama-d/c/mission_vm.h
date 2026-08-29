#ifndef MISSION_VM_H
#define MISSION_VM_H

#include <stdbool.h>
#include <stdint.h>

#include "conditions.h"
#include "geo.h"

#define MISSION_MAX_ITEMS        64u
#define MISSION_MAX_JUMP_SLOTS   16u
#define MISSION_MAX_TOTAL_JUMPS  256u   /* бюджет стрибків на політ */
#define MISSION_MAX_JUMP_DEPTH   2      /* глибина вкладеності циклів */
#define MISSION_ITEM_TIMEOUT_MS  120000u
#define MISSION_SERVO_CHANNELS   4u

/* Опкоди байткоду — це числа MAV_CMD: транслятор із MISSION_ITEM_INT
   лишається тривіальним, а байткод читається поруч із протоколом. */
typedef enum {
    OP_NAV_WAYPOINT       = 16,
    OP_NAV_LOITER_TIME    = 19,
    OP_NAV_RTL            = 20,
    OP_NAV_LAND           = 21,
    OP_NAV_TAKEOFF        = 22,
    OP_CONDITION_DELAY    = 112,
    OP_CONDITION_DISTANCE = 114,
    OP_CONDITION_YAW      = 115,
    OP_DO_JUMP            = 177,
    OP_DO_CHANGE_SPEED    = 178,
    OP_DO_SET_SERVO       = 183,
    OP_JUMP_IF_BAT_LOW    = 240   /* поза MAVLink: вендорний діапазон */
} mission_opcode_t;

#define ITEM_FLAG_AUTOCONTINUE 0x01u

/* Інструкція байткоду. Поля по порядку дають 18 значущих байтів,
   але між p2 та lat_e7 компілятор лишає 2 байти вирівнювання під
   int32 — саме тому інструкція важить рівно 20. */
typedef struct {
    uint8_t opcode;
    uint8_t flags;
    int16_t p1;
    int16_t p2;
    int32_t lat_e7;
    int32_t lon_e7;
    float   alt_m;
} mission_instr_t;

_Static_assert(sizeof(mission_instr_t) == 20,
               "інструкція місії мусить лишатися 20-байтною");

typedef enum {
    LOAD_OK = 0,
    LOAD_ERR_EMPTY,
    LOAD_ERR_TOO_MANY_ITEMS,
    LOAD_ERR_UNKNOWN_OPCODE,
    LOAD_ERR_BAD_JUMP_TARGET,   /* → MAV_MISSION_INVALID_PARAM1 */
    LOAD_ERR_BAD_PARAM,
    LOAD_ERR_TOO_MANY_JUMPS,
    LOAD_ERR_JUMP_TOO_DEEP
} mission_load_err_t;

typedef enum {
    VM_IDLE = 0,
    VM_RUNNING,
    VM_PAUSED,               /* autocontinue = 0: чекаємо команди з НСУ */
    VM_FINISHED,
    VM_ABORT_JUMP_BUDGET,
    VM_ABORT_ITEM_TIMEOUT,
    VM_ABORT_FAILSAFE
} vm_status_t;

/* Слот лічильника циклу. Живе ЛИШЕ в RAM: тримати залишок повторів
   у Flash означало б сотні перезаписів сектора за політ і зламаний
   повторний запуск тієї самої місії. */
typedef struct {
    uint16_t pc;
    int32_t  remaining;   /* -1 — нескінченний цикл */
    bool     used;
} jump_slot_t;

/* Те, що віртуальна машина віддає решті системи. Це прості дані,
   а не інтерфейс: контур навігації читає уставку, драйвер сервоприводів
   читає PWM. */
typedef struct {
    geo_point_t target;
    float       speed_mps;
    float       yaw_setpoint_deg;   /* <0 — курс не нав'язуємо */
    uint16_t    servo_pwm[MISSION_SERVO_CHANNELS];
} vm_outputs_t;

typedef struct {
    uint32_t    now_ms;
    geo_point_t position;
    float       yaw_deg;
    float       battery_v;
    float       battery_soc_pct;
    bool        gnss_ok;
    bool        link_ok;
} vm_telemetry_t;

typedef struct {
    mission_instr_t code[MISSION_MAX_ITEMS];
    uint16_t        len;

    /* Два паралельних показники стану — як у AP_Mission. */
    uint16_t        nav_pc;        /* активна NAV-команда */
    uint16_t        do_pc;         /* курсор конвеєра DO/CONDITION */
    bool            nav_active;
    bool            nav_reached;
    uint32_t        loiter_start_ms;

    condition_t     cond;
    jump_slot_t     jumps[MISSION_MAX_JUMP_SLOTS];
    uint16_t        total_jumps;

    uint32_t        item_start_ms;
    uint32_t        last_tick_ms;
    battery_filter_t bat;

    geo_point_t     home;
    vm_outputs_t    out;
    vm_status_t     status;
} mission_vm_t;

/* Рівень 1 захисту: статичний верифікатор при завантаженні.
   Місія, що не пройшла його, до Flash не потрапляє взагалі. */
mission_load_err_t mission_vm_load(mission_vm_t *vm,
                                   const mission_instr_t *prog, uint16_t len);

void mission_vm_start(mission_vm_t *vm, geo_point_t home, uint32_t now_ms);
void mission_vm_tick(mission_vm_t *vm, const vm_telemetry_t *t);

void mission_vm_resume(mission_vm_t *vm);                   /* MAV_CMD_MISSION_START */
void mission_vm_set_current(mission_vm_t *vm, uint16_t seq); /* MISSION_SET_CURRENT */

/* Аварія рівня 3: будь-яка апаратна відмова вища за код місії. */
void mission_vm_failsafe(mission_vm_t *vm);

bool mission_vm_stopped(const mission_vm_t *vm);

const char *mission_load_err_str(mission_load_err_t e);
const char *mission_vm_status_str(vm_status_t s);
const char *mission_opcode_str(uint8_t opcode);

#endif /* MISSION_VM_H */
