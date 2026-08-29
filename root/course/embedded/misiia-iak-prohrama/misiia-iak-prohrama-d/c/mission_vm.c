#include "mission_vm.h"

#include <math.h>
#include <string.h>

#define DEFAULT_ACCEPT_M   3.0f
#define DEFAULT_SPEED_MPS  12.0f
#define RTL_ALT_M          50.0f
#define TOUCHDOWN_ALT_M    0.3f
#define TAKEOFF_TOL_M      0.5f
#define BAT_MIN_V          14.2f   /* 4S, ~3.55 В на банку ПІСЛЯ фільтра */
#define BAT_TAU_S          3.0f

typedef enum {
    DO_NEXT,     /* виконано, крокуємо далі */
    DO_JUMPED,   /* do_pc уже переставлено */
    DO_HOLD,     /* чекаємо завершення поточної NAV-команди */
    DO_ABORT
} do_result_t;

/* ---------- класифікація опкодів ---------- */

static bool op_is_nav(uint8_t op)
{
    return op == OP_NAV_WAYPOINT || op == OP_NAV_LOITER_TIME ||
           op == OP_NAV_RTL || op == OP_NAV_LAND || op == OP_NAV_TAKEOFF;
}

static bool op_is_condition(uint8_t op)
{
    return op == OP_CONDITION_DELAY || op == OP_CONDITION_DISTANCE ||
           op == OP_CONDITION_YAW;
}

static bool op_is_jump(uint8_t op)
{
    return op == OP_DO_JUMP || op == OP_JUMP_IF_BAT_LOW;
}

static bool op_known(uint8_t op)
{
    return op_is_nav(op) || op_is_condition(op) || op_is_jump(op) ||
           op == OP_DO_CHANGE_SPEED || op == OP_DO_SET_SERVO;
}

static cond_kind_t cond_kind_of(uint8_t op)
{
    switch (op) {
        case OP_CONDITION_DELAY:    return COND_DELAY;
        case OP_CONDITION_DISTANCE: return COND_DISTANCE;
        case OP_CONDITION_YAW:      return COND_YAW;
        default:                    return COND_NONE;
    }
}

/* ---------- рівень 1: статичний верифікатор ---------- */

static mission_load_err_t lint_item(const mission_instr_t *in, uint16_t len)
{
    if (!op_known(in->opcode)) {
        return LOAD_ERR_UNKNOWN_OPCODE;
    }

    switch (in->opcode) {
        case OP_DO_JUMP:
            if (in->p1 < 0 || (uint16_t)in->p1 >= len) {
                return LOAD_ERR_BAD_JUMP_TARGET;
            }
            if (in->p2 < -1) {
                return LOAD_ERR_BAD_PARAM;
            }
            break;

        case OP_JUMP_IF_BAT_LOW:
            if (in->p2 < 0 || (uint16_t)in->p2 >= len) {
                return LOAD_ERR_BAD_JUMP_TARGET;
            }
            if (in->p1 <= 0 || in->p1 > 100) {
                return LOAD_ERR_BAD_PARAM;
            }
            break;

        case OP_DO_SET_SERVO:
            if (in->p1 < 1 || (uint16_t)in->p1 > MISSION_SERVO_CHANNELS) {
                return LOAD_ERR_BAD_PARAM;
            }
            if (in->p2 < 800 || in->p2 > 2200) {
                return LOAD_ERR_BAD_PARAM;
            }
            break;

        case OP_DO_CHANGE_SPEED:
            if (in->p2 <= 0 || in->p2 > 60) {
                return LOAD_ERR_BAD_PARAM;
            }
            break;

        case OP_CONDITION_DELAY:
        case OP_CONDITION_DISTANCE:
            if (in->p1 < 0) {
                return LOAD_ERR_BAD_PARAM;
            }
            break;

        default:
            break;
    }
    return LOAD_OK;
}

/* Зворотний стрибок i → t накриває інтервал [t, i]. Глибина вкладеності
   в точці x — скільки таких інтервалів її містять. */
static mission_load_err_t lint_jump_depth(const mission_instr_t *prog, uint16_t len)
{
    for (uint16_t x = 0; x < len; ++x) {
        int depth = 0;
        for (uint16_t i = 0; i < len; ++i) {
            if (prog[i].opcode != OP_DO_JUMP) {
                continue;
            }
            const uint16_t t = (uint16_t)prog[i].p1;
            if (t <= i && x >= t && x <= i) {
                ++depth;
            }
        }
        if (depth > MISSION_MAX_JUMP_DEPTH) {
            return LOAD_ERR_JUMP_TOO_DEEP;
        }
    }
    return LOAD_OK;
}

mission_load_err_t mission_vm_load(mission_vm_t *vm,
                                   const mission_instr_t *prog, uint16_t len)
{
    if (vm == NULL || prog == NULL || len == 0u) {
        return LOAD_ERR_EMPTY;
    }
    if (len > MISSION_MAX_ITEMS) {
        return LOAD_ERR_TOO_MANY_ITEMS;
    }

    uint16_t jumps = 0u;
    for (uint16_t i = 0; i < len; ++i) {
        const mission_load_err_t e = lint_item(&prog[i], len);
        if (e != LOAD_OK) {
            return e;
        }
        if (prog[i].opcode == OP_DO_JUMP) {
            ++jumps;
        }
    }
    if (jumps > MISSION_MAX_JUMP_SLOTS) {
        return LOAD_ERR_TOO_MANY_JUMPS;
    }

    const mission_load_err_t d = lint_jump_depth(prog, len);
    if (d != LOAD_OK) {
        return d;
    }

    memset(vm, 0, sizeof(*vm));
    memcpy(vm->code, prog, (size_t)len * sizeof(mission_instr_t));
    vm->len    = len;
    vm->status = VM_IDLE;
    return LOAD_OK;
}

/* ---------- навігаційна частина ---------- */

static float accept_radius(const mission_instr_t *in)
{
    return (in->p2 > 0) ? (float)in->p2 : DEFAULT_ACCEPT_M;
}

/* Нульові координати в MAVLink означають «тут же, де апарат». */
static geo_point_t item_point(const mission_instr_t *in, const vm_telemetry_t *t)
{
    geo_point_t p;
    p.lat_e7 = in->lat_e7;
    p.lon_e7 = in->lon_e7;
    p.alt_m  = in->alt_m;

    if (in->lat_e7 == 0 && in->lon_e7 == 0) {
        p.lat_e7 = t->position.lat_e7;
        p.lon_e7 = t->position.lon_e7;
    }
    return p;
}

/* Уставка навігаційного контуру для активної команди. Перераховується
   щотакту: посадка й повернення мають дві фази — спершу горизонталь,
   і лише над точкою — зниження. */
static void nav_update(mission_vm_t *vm, const vm_telemetry_t *t)
{
    const mission_instr_t *in = &vm->code[vm->nav_pc];
    const float r = accept_radius(in);
    const float r2 = r * r;
    geo_point_t p;

    switch (in->opcode) {
        case OP_NAV_RTL:
            p = vm->home;
            p.alt_m = (geo_dist_sq_m2(t->position, vm->home) > r2)
                        ? RTL_ALT_M : 0.0f;
            break;

        case OP_NAV_LAND:
            p = item_point(in, t);
            p.alt_m = (geo_dist_sq_m2(t->position, p) > r2)
                        ? t->position.alt_m : 0.0f;
            break;

        default:
            p = item_point(in, t);
            break;
    }
    vm->out.target = p;
}

static bool nav_complete(mission_vm_t *vm, const vm_telemetry_t *t)
{
    const mission_instr_t *in = &vm->code[vm->nav_pc];
    const float r = accept_radius(in);
    const float r2 = r * r;
    const float d2 = geo_dist_sq_m2(t->position, vm->out.target);

    switch (in->opcode) {
        case OP_NAV_TAKEOFF:
            return t->position.alt_m >= vm->out.target.alt_m - TAKEOFF_TOL_M;

        case OP_NAV_LAND:
        case OP_NAV_RTL:
            return d2 <= r2 && t->position.alt_m <= TOUCHDOWN_ALT_M;

        case OP_NAV_WAYPOINT:
        case OP_NAV_LOITER_TIME: {
            if (d2 > r2) {
                vm->nav_reached = false;
                return false;
            }
            /* p1 — час утримання над точкою, секунди. */
            const uint32_t hold_ms = (in->p1 > 0) ? (uint32_t)in->p1 * 1000u : 0u;
            if (!vm->nav_reached) {
                vm->nav_reached     = true;
                vm->loiter_start_ms = t->now_ms;
            }
            return (uint32_t)(t->now_ms - vm->loiter_start_ms) >= hold_ms;
        }

        default:
            return true;
    }
}

static void arm_nav(mission_vm_t *vm, uint16_t pc, const vm_telemetry_t *t)
{
    vm->nav_pc          = pc;
    vm->nav_active      = true;
    vm->nav_reached     = false;
    vm->loiter_start_ms = t->now_ms;
    vm->item_start_ms   = t->now_ms;   /* сторожовий таймер пункту */
    nav_update(vm, t);
}

/* ---------- зупинка місії ---------- */

static void abort_mission(mission_vm_t *vm, vm_status_t why)
{
    /* Рівень 3: VM більше нічого не веде, ціль забирає контур повернення. */
    vm->status           = why;
    vm->nav_active       = false;
    vm->cond.armed       = false;
    vm->out.target       = vm->home;
    vm->out.target.alt_m = RTL_ALT_M;
    vm->out.yaw_setpoint_deg = -1.0f;
}

void mission_vm_failsafe(mission_vm_t *vm)
{
    if (vm->status == VM_RUNNING || vm->status == VM_PAUSED) {
        abort_mission(vm, VM_ABORT_FAILSAFE);
    }
}

bool mission_vm_stopped(const mission_vm_t *vm)
{
    return vm->status == VM_FINISHED ||
           vm->status == VM_ABORT_JUMP_BUDGET ||
           vm->status == VM_ABORT_ITEM_TIMEOUT ||
           vm->status == VM_ABORT_FAILSAFE;
}

/* ---------- рівень 2: бюджет стрибків ---------- */

static jump_slot_t *jump_slot_for(mission_vm_t *vm, uint16_t pc, int32_t repeats)
{
    for (uint16_t i = 0; i < MISSION_MAX_JUMP_SLOTS; ++i) {
        if (vm->jumps[i].used && vm->jumps[i].pc == pc) {
            return &vm->jumps[i];
        }
    }
    for (uint16_t i = 0; i < MISSION_MAX_JUMP_SLOTS; ++i) {
        if (!vm->jumps[i].used) {
            /* Запису немає — заряджаємо слот повним repeat_count із Flash.
               Саме через це внутрішній цикл перезаряджається на кожному
               витку зовнішнього. */
            vm->jumps[i].pc        = pc;
            vm->jumps[i].remaining = repeats;
            vm->jumps[i].used      = true;
            return &vm->jumps[i];
        }
    }
    return NULL;   /* лінтер такого пропустити не мав */
}

static do_result_t exec_jump(mission_vm_t *vm, const mission_instr_t *in)
{
    jump_slot_t *slot = jump_slot_for(vm, vm->do_pc, (int32_t)in->p2);
    if (slot == NULL) {
        abort_mission(vm, VM_ABORT_JUMP_BUDGET);
        return DO_ABORT;
    }

    if (slot->remaining == 0) {
        /* Цикл вичерпано: запис інвалідуємо й виходимо на наступну інструкцію. */
        slot->used = false;
        return DO_NEXT;
    }

    if (vm->total_jumps >= MISSION_MAX_TOTAL_JUMPS) {
        abort_mission(vm, VM_ABORT_JUMP_BUDGET);
        return DO_ABORT;
    }

    if (slot->remaining > 0) {
        --slot->remaining;   /* -1 лишається -1: нескінченний цикл */
    }
    ++vm->total_jumps;
    vm->do_pc = (uint16_t)in->p1;
    return DO_JUMPED;
}

/* ---------- умови й миттєві дії ---------- */

static cond_ctx_t make_ctx(const mission_vm_t *vm, const vm_telemetry_t *t)
{
    cond_ctx_t c;
    c.now_ms          = t->now_ms;
    c.position        = t->position;
    c.next_waypoint   = vm->out.target;
    c.yaw_deg         = t->yaw_deg;
    c.battery_soc_pct = t->battery_soc_pct;
    return c;
}

static bool eval_condition(mission_vm_t *vm, const mission_instr_t *in,
                           const vm_telemetry_t *t)
{
    const cond_ctx_t ctx = make_ctx(vm, t);

    if (!vm->cond.armed) {
        condition_arm(&vm->cond, cond_kind_of(in->opcode),
                      (float)in->p1, (float)in->p2, &ctx);
    }
    if (vm->cond.kind == COND_YAW) {
        vm->out.yaw_setpoint_deg = condition_yaw_setpoint(&vm->cond, &ctx);
    }
    if (!condition_met(&vm->cond, &ctx)) {
        return false;   /* блокує ЛИШЕ чергу DO, апарат летить далі */
    }

    if (vm->cond.kind == COND_YAW) {
        vm->out.yaw_setpoint_deg = -1.0f;
    }
    vm->cond.armed = false;
    vm->cond.kind  = COND_NONE;
    return true;
}

static bool battery_low(const mission_vm_t *vm, const vm_telemetry_t *t,
                        float soc_threshold_pct)
{
    /* Основне джерело — SoC із кулонівського лічильника; фільтрована
       напруга страхує, поки лічильник не відкалібрований. Сира напруга
       не бере участі взагалі. */
    if (t->battery_soc_pct <= soc_threshold_pct) {
        return true;
    }
    return vm->bat.primed && vm->bat.value_v <= BAT_MIN_V;
}

static do_result_t exec_do(mission_vm_t *vm, const mission_instr_t *in,
                           const vm_telemetry_t *t)
{
    switch (in->opcode) {
        case OP_DO_CHANGE_SPEED:
            vm->out.speed_mps = (float)in->p2;
            return DO_NEXT;

        case OP_DO_SET_SERVO:
            /* Канал і межі PWM перевірив лінтер при завантаженні. */
            vm->out.servo_pwm[in->p1 - 1] = (uint16_t)in->p2;
            return DO_NEXT;

        case OP_JUMP_IF_BAT_LOW:
            /* Переходи чіпають навігаційну ціль, тому чекають, поки
               поточна NAV-команда завершиться. */
            if (vm->nav_active) {
                return DO_HOLD;
            }
            if (!battery_low(vm, t, (float)in->p1)) {
                return DO_NEXT;
            }
            vm->do_pc = (uint16_t)in->p2;
            return DO_JUMPED;

        case OP_DO_JUMP:
            if (vm->nav_active) {
                return DO_HOLD;
            }
            return exec_jump(vm, in);

        default:
            return DO_NEXT;
    }
}

/* Конвеєр допоміжних дій: за один такт вичитує все, що лежить між
   поточною NAV-командою та наступною, поки не впреться в незакриту
   умову або в чергову NAV. */
static void pump_do_queue(mission_vm_t *vm, const vm_telemetry_t *t)
{
    while (vm->do_pc < vm->len && vm->status == VM_RUNNING) {
        const mission_instr_t *in = &vm->code[vm->do_pc];

        if (op_is_nav(in->opcode)) {
            if (vm->nav_active) {
                return;   /* попередня ціль ще не досягнута */
            }
            arm_nav(vm, vm->do_pc, t);
            ++vm->do_pc;
            continue;     /* і одразу читаємо DO-хвіст за нею */
        }

        if (op_is_condition(in->opcode)) {
            if (!eval_condition(vm, in, t)) {
                return;
            }
            ++vm->do_pc;
            continue;
        }

        switch (exec_do(vm, in, t)) {
            case DO_NEXT:   ++vm->do_pc; break;
            case DO_JUMPED: break;
            case DO_HOLD:   return;
            case DO_ABORT:  return;
        }
    }
}

/* ---------- життєвий цикл ---------- */

void mission_vm_start(mission_vm_t *vm, geo_point_t home, uint32_t now_ms)
{
    vm->home            = home;
    vm->nav_pc          = 0u;
    vm->do_pc           = 0u;
    vm->nav_active      = false;
    vm->nav_reached     = false;
    vm->loiter_start_ms = now_ms;
    vm->total_jumps     = 0u;
    vm->item_start_ms   = now_ms;
    vm->last_tick_ms    = now_ms;

    /* Лічильники циклів існують лише в RAM — тому повторний старт
       тієї самої місії завжди має повний набір повторів. */
    memset(vm->jumps, 0, sizeof(vm->jumps));
    memset(&vm->cond, 0, sizeof(vm->cond));
    memset(&vm->out, 0, sizeof(vm->out));

    battery_filter_init(&vm->bat, BAT_TAU_S);

    vm->out.target           = home;
    vm->out.speed_mps        = DEFAULT_SPEED_MPS;
    vm->out.yaw_setpoint_deg = -1.0f;
    vm->status               = VM_RUNNING;
}

void mission_vm_resume(mission_vm_t *vm)
{
    if (vm->status == VM_PAUSED) {
        vm->status        = VM_RUNNING;
        vm->item_start_ms = vm->last_tick_ms;
    }
}

void mission_vm_set_current(mission_vm_t *vm, uint16_t seq)
{
    if (seq >= vm->len || mission_vm_stopped(vm)) {
        return;
    }
    vm->do_pc         = seq;
    vm->nav_active    = false;
    vm->cond.armed    = false;
    vm->cond.kind     = COND_NONE;
    vm->item_start_ms = vm->last_tick_ms;
    vm->status        = VM_RUNNING;
}

void mission_vm_tick(mission_vm_t *vm, const vm_telemetry_t *t)
{
    if (vm->status != VM_RUNNING && vm->status != VM_PAUSED) {
        return;
    }

    const float dt_s = (float)(uint32_t)(t->now_ms - vm->last_tick_ms) / 1000.0f;
    vm->last_tick_ms = t->now_ms;
    battery_filter_update(&vm->bat, t->battery_v, dt_s);

    /* Рівень 3 — перший за пріоритетом: апаратна відмова вища за місію. */
    if (!t->gnss_ok || !t->link_ok) {
        abort_mission(vm, VM_ABORT_FAILSAFE);
        return;
    }

    if (vm->status == VM_PAUSED) {
        /* autocontinue = 0: тримаємо зависання над досягнутою точкою
           й чекаємо MISSION_START або MISSION_SET_CURRENT з НСУ. */
        return;
    }

    /* Рівень 2 — таймаут на пункт: недосяжна умова не вішає місію назавжди. */
    if ((uint32_t)(t->now_ms - vm->item_start_ms) > MISSION_ITEM_TIMEOUT_MS) {
        abort_mission(vm, VM_ABORT_ITEM_TIMEOUT);
        return;
    }

    pump_do_queue(vm, t);
    if (vm->status != VM_RUNNING) {
        return;
    }

    if (vm->nav_active) {
        nav_update(vm, t);
        if (nav_complete(vm, t)) {
            const mission_instr_t *nav = &vm->code[vm->nav_pc];
            vm->nav_active = false;

            if (nav->opcode == OP_NAV_LAND || nav->opcode == OP_NAV_RTL) {
                vm->status = VM_FINISHED;
                return;
            }
            if ((nav->flags & ITEM_FLAG_AUTOCONTINUE) == 0u) {
                vm->status = VM_PAUSED;
                return;
            }
            pump_do_queue(vm, t);
        }
    }

    if (vm->status == VM_RUNNING && !vm->nav_active && vm->do_pc >= vm->len) {
        vm->status = VM_FINISHED;
    }
}

/* ---------- людські назви для журналу ---------- */

const char *mission_load_err_str(mission_load_err_t e)
{
    switch (e) {
        case LOAD_OK:                   return "прийнято";
        case LOAD_ERR_EMPTY:            return "порожня місія";
        case LOAD_ERR_TOO_MANY_ITEMS:   return "забагато пунктів";
        case LOAD_ERR_UNKNOWN_OPCODE:   return "невідомий опкод";
        case LOAD_ERR_BAD_JUMP_TARGET:  return "ціль переходу поза межами (INVALID_PARAM1)";
        case LOAD_ERR_BAD_PARAM:        return "неприпустимий параметр";
        case LOAD_ERR_TOO_MANY_JUMPS:   return "більше стрибків, ніж слотів у RAM";
        case LOAD_ERR_JUMP_TOO_DEEP:    return "занадто глибока вкладеність циклів";
        default:                        return "?";
    }
}

const char *mission_vm_status_str(vm_status_t s)
{
    switch (s) {
        case VM_IDLE:                return "очікує старту";
        case VM_RUNNING:             return "виконується";
        case VM_PAUSED:              return "пауза (autocontinue = 0)";
        case VM_FINISHED:            return "місію завершено";
        case VM_ABORT_JUMP_BUDGET:   return "АВАРІЯ: вичерпано бюджет стрибків";
        case VM_ABORT_ITEM_TIMEOUT:  return "АВАРІЯ: таймаут пункту";
        case VM_ABORT_FAILSAFE:      return "АВАРІЯ: failsafe перехопив керування";
        default:                     return "?";
    }
}

const char *mission_opcode_str(uint8_t opcode)
{
    switch (opcode) {
        case OP_NAV_WAYPOINT:       return "NAV_WAYPOINT";
        case OP_NAV_LOITER_TIME:    return "NAV_LOITER_TIME";
        case OP_NAV_RTL:            return "NAV_RETURN_TO_LAUNCH";
        case OP_NAV_LAND:           return "NAV_LAND";
        case OP_NAV_TAKEOFF:        return "NAV_TAKEOFF";
        case OP_CONDITION_DELAY:    return "CONDITION_DELAY";
        case OP_CONDITION_DISTANCE: return "CONDITION_DISTANCE";
        case OP_CONDITION_YAW:      return "CONDITION_YAW";
        case OP_DO_JUMP:            return "DO_JUMP";
        case OP_DO_CHANGE_SPEED:    return "DO_CHANGE_SPEED";
        case OP_DO_SET_SERVO:       return "DO_SET_SERVO";
        case OP_JUMP_IF_BAT_LOW:    return "JUMP_IF_BAT_LOW";
        default:                    return "?";
    }
}
