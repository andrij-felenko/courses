/* mission_vm.c — перевірка місії перед зльотом і сам інтерпретатор.
 *
 * Порядок читання: спершу дрібні предикати умов, далі таблиця лічильників
 * циклів, далі завантажувач із перевірками, і аж тоді mission_vm_step().
 */
#include "mission_vm.h"

#include <math.h>
#include <string.h>

/* ------------------------------------------------------------------ умови */

/* Звести різницю кутів у діапазон [−180; 180]. Робиться арифметикою, а не
 * циклом «поки більше 180 — відняти 360»: на зіпсованому вході (курс у
 * мільйон градусів, NaN) такий цикл крутився б невизначено довго, а крок
 * машини мусить коштувати сталий час. */
static float vm_wrap_180(float deg)
{
    if (!isfinite(deg)) {
        return NAN;
    }
    float w = fmodf(deg + 180.0f, 360.0f);
    if (w < 0.0f) {
        w += 360.0f;
    }
    return w - 180.0f;
}

/* Різниця беззнакових лічильників коректна й тоді, коли 32-бітний лічильник
 * тиків переповнився (це стається кожні 49,7 доби безперервної роботи). */
static bool vm_time_elapsed(uint32_t start_ms, uint32_t now_ms, uint32_t delay_ms)
{
    return (uint32_t)(now_ms - start_ms) >= delay_ms;
}

/* Чи придатна позиція до навігаційних рішень. NaN у відстані — це рівно те,
 * що приходить, коли GNSS відмовив або оцінювач розійшовся. */
static bool vm_position_valid(const vm_telemetry_t *telem)
{
    return isfinite(telem->dist_to_wp_m);
}

/* Хибна позиція ніколи не дає «так»: машина лишиться в очікуванні, доки
 * супервізор не вирішить інакше. Прапорець навігатора теж без позиції не
 * приймаємо — він міг застаріти. */
static bool vm_waypoint_reached(const vm_telemetry_t *telem, float radius_m)
{
    if (!vm_position_valid(telem)) {
        return false;
    }
    return telem->wp_reached || telem->dist_to_wp_m <= radius_m;
}

static bool vm_yaw_reached(float current_deg, float target_deg, float tolerance_deg)
{
    float diff = vm_wrap_180(current_deg - target_deg);
    if (!isfinite(diff)) {
        return false;
    }
    return fabsf(diff) <= tolerance_deg;
}

/* ------------------------------------------- лічильники повторів DO_JUMP */

static vm_loop_slot_t *vm_loop_acquire(mission_vm_t *vm, uint16_t jump_pc, uint16_t repeats)
{
    for (unsigned i = 0; i < VM_MAX_LOOP_SLOTS; i++) {
        if (vm->loops[i].active && vm->loops[i].jump_pc == jump_pc) {
            return &vm->loops[i];
        }
    }
    for (unsigned i = 0; i < VM_MAX_LOOP_SLOTS; i++) {
        if (!vm->loops[i].active) {
            vm->loops[i].active    = true;
            vm->loops[i].jump_pc   = jump_pc;
            vm->loops[i].remaining = repeats;
            return &vm->loops[i];
        }
    }
    /* Недосяжно у справній програмі: завантажувач порахував DO_JUMP-и наперед
     * і відхилив би місію, у якій їх більше за слоти. */
    return NULL;
}

/* Слот вичерпаного циклу саме звільняємо, а не лишаємо з нулем: коли зовнішній
 * цикл заведе внутрішній на друге коло, той мусить почати рахувати спочатку. */
static void vm_loop_release(mission_vm_t *vm, uint16_t jump_pc)
{
    for (unsigned i = 0; i < VM_MAX_LOOP_SLOTS; i++) {
        if (vm->loops[i].active && vm->loops[i].jump_pc == jump_pc) {
            vm->loops[i].active = false;
            return;
        }
    }
}

/* ------------------------------------------------------- завантаження */

static bool vm_opcode_known(uint8_t opcode)
{
    switch ((vm_opcode_t)opcode) {
    case OP_HALT:
    case OP_NAV_TAKEOFF:
    case OP_NAV_WAYPOINT:
    case OP_NAV_LAND:
    case OP_NAV_RTL:
    case OP_DO_SET_SERVO:
    case OP_DO_CHANGE_SPEED:
    case OP_DO_JUMP:
    case OP_JUMP_IF_BAT_LOW:
    case OP_COND_DELAY:
    case OP_COND_DISTANCE:
    case OP_COND_YAW:
        return true;
    default:
        return false;
    }
}

/* Інструкція, після якої виконання не продовжується. Місія мусить закінчуватися
 * однією з них — інакше машина просто добігла б кінця масиву, і читач байткоду
 * не відрізнив би завершену програму від обрізаної при передаванні. */
static bool vm_is_terminator(uint8_t opcode)
{
    return opcode == OP_HALT || opcode == OP_NAV_LAND || opcode == OP_NAV_RTL;
}

static vm_load_result_t vm_validate(const vm_instruction_t *code, uint16_t len)
{
    unsigned loop_count = 0;

    for (uint16_t i = 0; i < len; i++) {
        const vm_instruction_t *in = &code[i];

        if (!vm_opcode_known(in->opcode)) {
            return VM_LOAD_BAD_OPCODE;
        }

        switch ((vm_opcode_t)in->opcode) {
        case OP_NAV_TAKEOFF:
            if (!isfinite(in->alt_m) || in->alt_m <= 0.0f) {
                return VM_LOAD_BAD_PARAM;
            }
            break;

        case OP_NAV_WAYPOINT:
            if (!isfinite(in->alt_m)) {
                return VM_LOAD_BAD_PARAM;
            }
            /* Координати поза глобусом означають зіпсоване передавання. */
            if (in->lat_1e7 < -900000000 || in->lat_1e7 > 900000000 ||
                in->lon_1e7 < -1800000000 || in->lon_1e7 > 1800000000) {
                return VM_LOAD_BAD_PARAM;
            }
            break;

        case OP_DO_SET_SERVO:
            if (in->param1 < 1 || in->param1 > 16) {
                return VM_LOAD_BAD_PARAM;
            }
            if (in->param2 < 800 || in->param2 > 2200) {
                return VM_LOAD_BAD_PARAM;
            }
            break;

        case OP_DO_CHANGE_SPEED:
            if (in->param2 < 10 || in->param2 > 3000) {
                return VM_LOAD_BAD_PARAM;
            }
            break;

        case OP_DO_JUMP:
            if (in->param1 < 0 || in->param1 >= (int16_t)len) {
                return VM_LOAD_BAD_JUMP;
            }
            if (in->param2 < 1) {
                return VM_LOAD_BAD_PARAM;
            }
            loop_count++;
            if (loop_count > VM_MAX_LOOP_SLOTS) {
                return VM_LOAD_TOO_MANY_LOOPS;
            }
            break;

        case OP_JUMP_IF_BAT_LOW:
            if (in->param1 < 1 || in->param1 > 99) {
                return VM_LOAD_BAD_PARAM;
            }
            if (in->param2 < 0 || in->param2 >= (int16_t)len) {
                return VM_LOAD_BAD_JUMP;
            }
            break;

        case OP_COND_DELAY:
            if (in->param1 < 0 || in->param1 > 3600) {
                return VM_LOAD_BAD_PARAM;
            }
            break;

        case OP_COND_DISTANCE:
            if (in->param1 <= 0) {
                return VM_LOAD_BAD_PARAM;
            }
            break;

        case OP_COND_YAW:
            if (in->param1 < -180 || in->param1 > 360) {
                return VM_LOAD_BAD_PARAM;
            }
            break;

        default:
            break;
        }
    }

    if (!vm_is_terminator(code[len - 1].opcode)) {
        return VM_LOAD_NO_TERMINATOR;
    }
    return VM_LOAD_OK;
}

void mission_vm_init(mission_vm_t *vm)
{
    memset(vm, 0, sizeof(*vm));
    vm->status = VM_STATUS_IDLE;
}

void mission_vm_set_home(mission_vm_t *vm, int32_t lat_1e7, int32_t lon_1e7, float alt_m)
{
    vm->home.lat_1e7 = lat_1e7;
    vm->home.lon_1e7 = lon_1e7;
    vm->home.alt_m   = alt_m;
    vm->home_set     = true;
}

vm_load_result_t mission_vm_load(mission_vm_t *vm, const vm_instruction_t *code, uint16_t len)
{
    if (len == 0 || code == NULL) {
        return VM_LOAD_EMPTY;
    }
    if (len > VM_MAX_INSTRUCTIONS) {
        return VM_LOAD_TOO_LONG;
    }
    if (!vm->home_set) {
        return VM_LOAD_NO_HOME;
    }

    vm_load_result_t verdict = vm_validate(code, len);
    if (verdict != VM_LOAD_OK) {
        return verdict;
    }

    vm->program        = code;
    vm->program_len    = len;
    vm->pc             = 0;
    vm->status         = VM_STATUS_RUNNING;
    vm->entered        = false;
    vm->instr_entry_ms = 0;
    vm->total_jumps    = 0;
    vm->steps_executed = 0;
    memset(vm->loops, 0, sizeof(vm->loops));
    return VM_LOAD_OK;
}

/* ------------------------------------------------------------ інтерпретатор */

bool mission_vm_is_error(vm_status_t status)
{
    return status == VM_STATUS_ERROR_INFINITE_LOOP ||
           status == VM_STATUS_ERROR_OUT_OF_BOUNDS ||
           status == VM_STATUS_ERROR_INVALID_OPCODE;
}

bool mission_vm_is_active(vm_status_t status)
{
    return status == VM_STATUS_RUNNING ||
           status == VM_STATUS_WAITING_NAV ||
           status == VM_STATUS_WAITING_COND;
}

uint32_t mission_vm_wait_elapsed_ms(const mission_vm_t *vm, uint32_t now_ms)
{
    if (!vm->entered) {
        return 0;
    }
    return (uint32_t)(now_ms - vm->instr_entry_ms);
}

/* Аварійна зупинка: знімаємо чинні уставки, щоб апарат не летів далі за
 * інерцією плану, і піднімаємо прапорець супервізорові Failsafe. Рішення про
 * посадку чи повернення ухвалює він — машина своє вже сказала. */
static void vm_fail(mission_vm_t *vm, vm_actuators_t *act, vm_status_t status)
{
    vm->status             = status;
    act->nav_valid         = false;
    act->target_speed_mps  = 0.0f;
    act->failsafe_request  = true;
}

/* Висота уставки завжди віддається назовні відносно домашньої точки: саме в
 * цій системі відліку працює контур висоти. Прапорець VM_FLAG_ALT_ABSOLUTE
 * каже, що в байткоді записано висоту над рівнем моря. */
static float vm_target_alt_rel(const mission_vm_t *vm, const vm_instruction_t *in)
{
    if (in->flags & VM_FLAG_ALT_ABSOLUTE) {
        return in->alt_m - vm->home.alt_m;
    }
    return in->alt_m;
}

static void vm_advance(mission_vm_t *vm)
{
    vm->pc++;
    vm->status = VM_STATUS_RUNNING;
}

vm_status_t mission_vm_step(mission_vm_t       *vm,
                            const vm_telemetry_t *telem,
                            vm_actuators_t       *act,
                            uint32_t              now_ms)
{
    if (!mission_vm_is_active(vm->status)) {
        return vm->status;
    }
    if (vm->pc >= vm->program_len) {
        vm->status = VM_STATUS_COMPLETED;
        return vm->status;
    }

    const vm_instruction_t *in          = &vm->program[vm->pc];
    const uint16_t          pc_before   = vm->pc;
    const bool              first_visit = !vm->entered;

    if (first_visit) {
        vm->entered        = true;
        vm->instr_entry_ms = now_ms;
    }
    vm->steps_executed++;

    switch ((vm_opcode_t)in->opcode) {
    case OP_HALT:
        act->nav_valid = false;
        vm->status     = VM_STATUS_COMPLETED;
        break;

    case OP_NAV_TAKEOFF:
        if (first_visit) {
            act->nav_valid      = true;
            act->target_lat_1e7 = vm->home.lat_1e7;
            act->target_lon_1e7 = vm->home.lon_1e7;
            act->target_alt_m   = vm_target_alt_rel(vm, in);
            vm->status          = VM_STATUS_WAITING_NAV;
        }
        if (in->flags & VM_FLAG_AUTO_CONTINUE) {
            vm_advance(vm);
            break;
        }
        if (isfinite(telem->alt_m) &&
            telem->alt_m >= act->target_alt_m * VM_TAKEOFF_ALT_FRACTION) {
            vm_advance(vm);
        }
        break;

    case OP_NAV_WAYPOINT:
        if (first_visit) {
            act->nav_valid      = true;
            act->target_lat_1e7 = in->lat_1e7;
            act->target_lon_1e7 = in->lon_1e7;
            act->target_alt_m   = vm_target_alt_rel(vm, in);
            vm->status          = VM_STATUS_WAITING_NAV;
        }
        /* AUTO_CONTINUE: уставку видано — і одразу далі. Апарат летить до
         * точки, а програма тим часом стоїть на наступній інструкції: так
         * умова «за 30 метрів до точки» встигає спрацювати в дорозі. */
        if (in->flags & VM_FLAG_AUTO_CONTINUE) {
            vm_advance(vm);
            break;
        }
        /* Позиції немає — лишаємося в WAITING_NAV скільки завгодно довго.
         * Таймаут не наша справа: його міряє супервізор за
         * mission_vm_wait_elapsed_ms(). */
        if (vm_waypoint_reached(telem, VM_WAYPOINT_RADIUS_M)) {
            vm_advance(vm);
        }
        break;

    case OP_NAV_LAND:
        act->nav_valid      = true;
        act->target_lat_1e7 = telem->lat_1e7;
        act->target_lon_1e7 = telem->lon_1e7;
        act->target_alt_m   = 0.0f;
        act->land_triggered = true;
        vm->status          = VM_STATUS_COMPLETED;
        break;

    case OP_NAV_RTL:
        act->nav_valid      = true;
        act->target_lat_1e7 = vm->home.lat_1e7;
        act->target_lon_1e7 = vm->home.lon_1e7;
        act->target_alt_m   = VM_RTL_ALT_M;
        act->rtl_triggered  = true;
        vm->status          = VM_STATUS_COMPLETED;
        break;

    case OP_DO_SET_SERVO:
        act->servo_channel = (uint8_t)in->param1;
        act->servo_pwm_us  = (uint16_t)in->param2;
        vm_advance(vm);
        break;

    case OP_DO_CHANGE_SPEED:
        act->target_speed_mps = (float)in->param2 * 0.01f;
        vm_advance(vm);
        break;

    case OP_DO_JUMP: {
        /* Бюджет перевіряємо ПЕРЕД стрибком: інакше остання дозволена ітерація
         * встигла б піти на друге коло. */
        if (vm->total_jumps >= VM_MAX_TOTAL_JUMPS) {
            vm_fail(vm, act, VM_STATUS_ERROR_INFINITE_LOOP);
            break;
        }
        vm_loop_slot_t *slot = vm_loop_acquire(vm, vm->pc, (uint16_t)in->param2);
        if (slot == NULL) {
            vm_fail(vm, act, VM_STATUS_ERROR_OUT_OF_BOUNDS);
            break;
        }
        if (slot->remaining > 0) {
            slot->remaining--;
            vm->total_jumps++;
            vm->pc     = (uint16_t)in->param1;
            vm->status = VM_STATUS_RUNNING;
        } else {
            vm_loop_release(vm, vm->pc);
            vm_advance(vm);
        }
        break;
    }

    case OP_JUMP_IF_BAT_LOW:
        /* NaN у заряді дає «ні» на будь-яке порівняння — програма йде далі,
         * а рішення про несправний датчик ухвалює супервізор. */
        if (telem->battery_soc_pct < (float)in->param1) {
            if (vm->total_jumps >= VM_MAX_TOTAL_JUMPS) {
                vm_fail(vm, act, VM_STATUS_ERROR_INFINITE_LOOP);
                break;
            }
            vm->total_jumps++;
            vm->pc     = (uint16_t)in->param2;
            vm->status = VM_STATUS_RUNNING;
        } else {
            vm_advance(vm);
        }
        break;

    case OP_COND_DELAY:
        vm->status = VM_STATUS_WAITING_COND;
        if (vm_time_elapsed(vm->instr_entry_ms, now_ms, (uint32_t)in->param1 * 1000u)) {
            vm_advance(vm);
        }
        break;

    case OP_COND_DISTANCE:
        vm->status = VM_STATUS_WAITING_COND;
        if (vm_position_valid(telem) && telem->dist_to_wp_m <= (float)in->param1) {
            vm_advance(vm);
        }
        break;

    case OP_COND_YAW:
        vm->status = VM_STATUS_WAITING_COND;
        if (vm_yaw_reached(telem->yaw_deg, (float)in->param1, VM_YAW_TOLERANCE_DEG)) {
            vm_advance(vm);
        }
        break;

    default:
        /* Сюди можна потрапити лише тоді, коли байткод зіпсувався вже після
         * завантаження — наприклад, збій Flash. Перевірка коштує один порівняльний
         * перехід, а мовчазне виконання чужого байта коштувало б апарата. */
        vm_fail(vm, act, VM_STATUS_ERROR_INVALID_OPCODE);
        break;
    }

    /* Пішли на іншу інструкцію — її одноразові дії ще попереду. */
    if (vm->pc != pc_before) {
        vm->entered = false;
    }
    /* Дійшли до кінця масиву без термінатора може лише DO_JUMP на останню
     * інструкцію; наступний крок закриє програму. */
    return vm->status;
}

/* ----------------------------------------------------------------- імена */

const char *vm_status_name(vm_status_t status)
{
    switch (status) {
    case VM_STATUS_IDLE:                 return "IDLE";
    case VM_STATUS_RUNNING:              return "RUNNING";
    case VM_STATUS_WAITING_NAV:          return "WAITING_NAV";
    case VM_STATUS_WAITING_COND:         return "WAITING_COND";
    case VM_STATUS_COMPLETED:            return "COMPLETED";
    case VM_STATUS_ERROR_INFINITE_LOOP:  return "ERROR_INFINITE_LOOP";
    case VM_STATUS_ERROR_OUT_OF_BOUNDS:  return "ERROR_OUT_OF_BOUNDS";
    case VM_STATUS_ERROR_INVALID_OPCODE: return "ERROR_INVALID_OPCODE";
    default:                             return "?";
    }
}

const char *vm_load_result_name(vm_load_result_t result)
{
    switch (result) {
    case VM_LOAD_OK:              return "OK";
    case VM_LOAD_EMPTY:           return "EMPTY";
    case VM_LOAD_TOO_LONG:        return "TOO_LONG";
    case VM_LOAD_NO_HOME:         return "NO_HOME";
    case VM_LOAD_BAD_OPCODE:      return "BAD_OPCODE";
    case VM_LOAD_BAD_PARAM:       return "BAD_PARAM";
    case VM_LOAD_BAD_JUMP:        return "BAD_JUMP";
    case VM_LOAD_TOO_MANY_LOOPS:  return "TOO_MANY_LOOPS";
    case VM_LOAD_NO_TERMINATOR:   return "NO_TERMINATOR";
    default:                      return "?";
    }
}
