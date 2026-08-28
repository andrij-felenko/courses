#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define VM_MAX_INSTRUCTIONS   64
#define VM_MAX_JUMP_SLOTS     16
#define VM_MAX_TOTAL_JUMPS    256
#define VM_WAYPOINT_RADIUS_M  2.0f

typedef enum {
    OP_HALT             = 0x00,
    OP_NAV_TAKEOFF      = 0x01,
    OP_NAV_WAYPOINT     = 0x02,
    OP_NAV_LAND         = 0x03,
    OP_NAV_RTL          = 0x04,
    OP_DO_SET_SERVO     = 0x10,
    OP_DO_CHANGE_SPEED  = 0x11,
    OP_DO_JUMP          = 0x20,
    OP_JUMP_IF_BAT_LOW  = 0x21,
    OP_COND_DELAY       = 0x30,
    OP_COND_DISTANCE    = 0x31,
    OP_COND_YAW         = 0x32
} vm_opcode_t;

typedef struct {
    vm_opcode_t opcode;
    uint8_t     flags;
    int16_t     param1;   /* час (с), канал, кут (град), % батареї */
    int16_t     param2;   /* repeats, pwm, швидкість (см/с) */
    int32_t     lat_1e7;  /* широта * 10^7 або зміщення */
    int32_t     lon_1e7;  /* довгота * 10^7 */
    float       alt_m;    /* висота (метри) */
} vm_instruction_t;

typedef struct {
    float   lat_deg;
    float   lon_deg;
    float   alt_m;
    float   yaw_deg;
    float   dist_to_wp_m;
    float   battery_soc_pct;
    bool    wp_reached;
} vm_telemetry_t;

typedef struct {
    bool    nav_valid;
    float   target_lat;
    float   target_lon;
    float   target_alt;
    float   target_speed_mps;
    uint8_t servo_channel;
    uint16_t servo_pwm;
    bool    rtl_triggered;
    bool    land_triggered;
} vm_actuators_t;

typedef enum {
    VM_STATUS_IDLE,
    VM_STATUS_RUNNING,
    VM_STATUS_WAITING_NAV,
    VM_STATUS_WAITING_COND,
    VM_STATUS_COMPLETED,
    VM_STATUS_ERROR_INFINITE_LOOP,
    VM_STATUS_ERROR_OUT_OF_BOUNDS,
    VM_STATUS_ERROR_INVALID_OPCODE
} vm_status_t;

typedef struct {
    uint8_t  target_pc;
    uint16_t remaining_iterations;
    bool     active;
} vm_jump_slot_t;

typedef struct {
    vm_instruction_t program[VM_MAX_INSTRUCTIONS];
    uint16_t         program_len;
    uint16_t         pc;
    vm_status_t      status;
    uint32_t         cond_start_time_ms;
    uint32_t         total_jumps_executed;
    vm_jump_slot_t   jump_table[VM_MAX_JUMP_SLOTS];
} mission_vm_t;

void mission_vm_init(mission_vm_t *vm) {
    memset(vm, 0, sizeof(mission_vm_t));
    vm->status = VM_STATUS_IDLE;
}

bool mission_vm_load(mission_vm_t *vm, const vm_instruction_t *code, uint16_t len) {
    if (len > VM_MAX_INSTRUCTIONS) {
        return false;
    }
    memcpy(vm->program, code, len * sizeof(vm_instruction_t));
    vm->program_len = len;
    vm->pc = 0;
    vm->status = VM_STATUS_RUNNING;
    vm->cond_start_time_ms = 0;
    vm->total_jumps_executed = 0;
    memset(vm->jump_table, 0, sizeof(vm->jump_table));
    return true;
}

static vm_jump_slot_t* get_jump_slot(mission_vm_t *vm, uint16_t pc, uint8_t target, uint16_t initial_cnt) {
    for (int i = 0; i < VM_MAX_JUMP_SLOTS; i++) {
        if (vm->jump_table[i].active && vm->jump_table[i].target_pc == target) {
            return &vm->jump_table[i];
        }
    }
    for (int i = 0; i < VM_MAX_JUMP_SLOTS; i++) {
        if (!vm->jump_table[i].active) {
            vm->jump_table[i].active = true;
            vm->jump_table[i].target_pc = target;
            vm->jump_table[i].remaining_iterations = initial_cnt;
            return &vm->jump_table[i];
        }
    }
    return NULL;
}

vm_status_t mission_vm_step(mission_vm_t *vm,
                            const vm_telemetry_t *telem,
                            vm_actuators_t *act,
                            uint32_t now_ms)
{
    if (vm->status != VM_STATUS_RUNNING &&
        vm->status != VM_STATUS_WAITING_NAV &&
        vm->status != VM_STATUS_WAITING_COND) {
        return vm->status;
    }

    if (vm->pc >= vm->program_len) {
        vm->status = VM_STATUS_COMPLETED;
        return vm->status;
    }

    const vm_instruction_t *instr = &vm->program[vm->pc];

    switch (instr->opcode) {
        case OP_HALT:
            vm->status = VM_STATUS_COMPLETED;
            break;

        case OP_NAV_TAKEOFF:
        case OP_NAV_WAYPOINT:
            if (vm->status != VM_STATUS_WAITING_NAV) {
                act->nav_valid = true;
                act->target_lat = (float)instr->lat_1e7 * 1e-7f;
                act->target_lon = (float)instr->lon_1e7 * 1e-7f;
                act->target_alt = instr->alt_m;
                vm->status = VM_STATUS_WAITING_NAV;
            }
            if (telem->wp_reached || telem->dist_to_wp_m <= VM_WAYPOINT_RADIUS_M) {
                vm->pc++;
                vm->status = VM_STATUS_RUNNING;
            }
            break;

        case OP_NAV_LAND:
            act->land_triggered = true;
            vm->status = VM_STATUS_COMPLETED;
            break;

        case OP_NAV_RTL:
            act->rtl_triggered = true;
            vm->status = VM_STATUS_COMPLETED;
            break;

        case OP_DO_SET_SERVO:
            act->servo_channel = (uint8_t)instr->param1;
            act->servo_pwm = (uint16_t)instr->param2;
            vm->pc++;
            break;

        case OP_DO_CHANGE_SPEED:
            act->target_speed_mps = (float)instr->param2 * 0.01f;
            vm->pc++;
            break;

        case OP_DO_JUMP: {
            uint8_t target = (uint8_t)instr->param1;
            uint16_t repeats = (uint16_t)instr->param2;

            if (target >= vm->program_len) {
                vm->status = VM_STATUS_ERROR_OUT_OF_BOUNDS;
                break;
            }

            if (vm->total_jumps_executed >= VM_MAX_TOTAL_JUMPS) {
                vm->status = VM_STATUS_ERROR_INFINITE_LOOP;
                break;
            }

            vm_jump_slot_t *slot = get_jump_slot(vm, vm->pc, target, repeats);
            if (!slot) {
                vm->status = VM_STATUS_ERROR_OUT_OF_BOUNDS;
                break;
            }

            if (slot->remaining_iterations > 0) {
                slot->remaining_iterations--;
                vm->total_jumps_executed++;
                vm->pc = target;
            } else {
                slot->active = false;
                vm->pc++;
            }
            break;
        }

        case OP_JUMP_IF_BAT_LOW: {
            float threshold_pct = (float)instr->param1;
            uint8_t target = (uint8_t)instr->param2;

            if (telem->battery_soc_pct < threshold_pct) {
                if (target >= vm->program_len) {
                    vm->status = VM_STATUS_ERROR_OUT_OF_BOUNDS;
                } else {
                    vm->pc = target;
                }
            } else {
                vm->pc++;
            }
            break;
        }

        case OP_COND_DELAY: {
            uint32_t delay_ms = (uint32_t)instr->param1 * 1000U;
            if (vm->status != VM_STATUS_WAITING_COND) {
                vm->cond_start_time_ms = now_ms;
                vm->status = VM_STATUS_WAITING_COND;
            }
            if ((now_ms - vm->cond_start_time_ms) >= delay_ms) {
                vm->pc++;
                vm->status = VM_STATUS_RUNNING;
            }
            break;
        }

        case OP_COND_DISTANCE: {
            float target_dist = (float)instr->param1;
            if (telem->dist_to_wp_m <= target_dist) {
                vm->pc++;
                vm->status = VM_STATUS_RUNNING;
            } else {
                vm->status = VM_STATUS_WAITING_COND;
            }
            break;
        }

        case OP_COND_YAW: {
            float target_yaw = (float)instr->param1;
            float diff = telem->yaw_deg - target_yaw;
            while (diff < -180.0f) diff += 360.0f;
            while (diff > 180.0f) diff -= 360.0f;
            if (diff < 0.0f) diff = -diff;

            if (diff <= 5.0f) {
                vm->pc++;
                vm->status = VM_STATUS_RUNNING;
            } else {
                vm->status = VM_STATUS_WAITING_COND;
            }
            break;
        }

        default:
            vm->status = VM_STATUS_ERROR_INVALID_OPCODE;
            break;
    }

    return vm->status;
}
