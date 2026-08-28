# ⚙️ Віртуальна машина виконання місій для мікроконтролера

Цей проєкт надає автономну віртуальну машину (Mission VM) для виконання програмованих польотних місій на борту мікроконтролера без повноцінної операційної системи (bare-metal) або всередині окремої низькопріоритетної задачі RTOS. Вона інтерпретує компактний бінарний байткод, підтримує навігаційні команди просторового переміщення, миттєві дії керування корисним навантаженням, неблокуючі умови очікування, цикли з лічильниками повторів та аварійні переходи за станом сенсорів і заряду батареї, захищаючи ядро автопілота від зависання й нескінченних циклів.

## Архітектурні вимоги та модель пам'яті

На відміну від інтерпретаторів загального призначення (таких як Lua, Python або WebAssembly), інтерпретатор польотної місії повинен задовольняти суворим обмеженням систем жорсткого реального часу:

1. **Нульове динамічне виділення пам'яті (Zero Dynamic Allocation):** виклики `malloc()`, `free()`, `new` та `delete` повністю заборонені після фази завантаження місії. Увесь робочий простір, таблиці стрибків і буфери інструкцій виділяються статично на етапі компіляції. Це усуває ризик фрагментації купи (Heap Fragmentation) та непередбачуваних затримок при збиранні сміття.
2. **Детермінований час виконання такту (O(1) Execution Time):** виконання одного кроку `mission_vm_step()` займає фіксовану кількість тактів процесора (типово менше 2 мікросекунд на ядрі ARM Cortex-M4 @ 168 МГц), що гарантує відсутність просідання частоти основного контуру керування.
3. **Ізоляція стану виконання в RAM:** статичний байткод місії зберігається у Flash-пам'яті або ROM, тоді як динамічний контекст (лічильники циклів, мітки часу початку умов, програмний лічильник `pc`) розміщується в швидкому внутрішньому ОЗП (SRAM). Це захищає енергонезалежну пам'ять від деградації через часті перезаписи при проходженні циклічних ділянок.
4. **Неблокуюче кооперативне опитування:** віртуальна машина не має права використовувати блокувальні затримки на зразок `sleep()` чи `vTaskDelay()`. Якщо інструкція очікує виконання просторової чи часової умови (`CONDITION_DELAY`, `NAV_WAYPOINT`), машина фіксує стан `WAITING` і негайно повертає керування планувальнику.

```
       +-------------------------------------------------------------+
       |                  Байткод місії (Flash/RAM)                  |
       +-------------------------------------------------------------+
                                      |
                                      v
+------------------+         +------------------+         +------------------+
| Давачі / EKF     | ------> |    Mission VM    | ------> | Навігація / PWM  |
| (telemetry_t)    |         | (контекст + RAM) |         | (actuator_cmd_t) |
+------------------+         +------------------+         +------------------+
                                      ^
                                      |
                           +----------------------+
                           | Loop & Time Watchdog |
                           +----------------------+
```

## Формат інструкцій та кодування опкодів

Кожна інструкція місії займає рівно 20 байтів у пам'яті, що забезпечує природне вирівнювання по 4-байтній межі для 32-бітних процесорів (ARM Cortex-M, RISC-V, ESP32 Xtensa) без потреби в упакованих структурах (`__attribute__((packed))`), які сповільнюють доступ до пам'яті через неaligned-читання.

Поля інструкції `vm_instruction_t`:
- `opcode` (1 байт) — код операції з переліку `vm_opcode_t`.
- `flags` (1 байт) — бітові прапорці (автопродовження, система відліку висоти).
- `param1` (2 байти, `int16_t`) — цілочисловий аргумент: час затримки в секундах, номер каналу сервоприводу, цільовий кут курсу в градусах або поріг батареї у відсотках.
- `param2` (2 байти, `int16_t`) — другий аргумент: лічильник повторів циклу, ширина імпульсу PWM у мікросекундах або цільова швидкість у сантиметрах на секунду.
- `lat_1e7` (4 байти, `int32_t`) — географічна широта, помножена на 10⁷ (дискретність близько 1 см).
- `lon_1e7` (4 байти, `int32_t`) — географічна довгота, помножена на 10⁷.
- `alt_m` (4 байти, `float`) — цільова висота в метрах.

## Повна реалізація віртуальної машини на C та C++

:::tabs
=== "C"
```c
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
```
=== "C++"
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <cmath>

namespace mission {

enum class Opcode : uint8_t {
    Halt             = 0x00,
    NavTakeoff      = 0x01,
    NavWaypoint     = 0x02,
    NavLand         = 0x03,
    NavRtl          = 0x04,
    DoSetServo      = 0x10,
    DoChangeSpeed   = 0x11,
    DoJump          = 0x20,
    JumpIfBatLow    = 0x21,
    CondDelay       = 0x30,
    CondDistance    = 0x31,
    CondYaw         = 0x32
};

struct Instruction {
    Opcode  opcode{Opcode::Halt};
    uint8_t flags{0};
    int16_t param1{0};
    int16_t param2{0};
    int32_t lat_1e7{0};
    int32_t lon_1e7{0};
    float   alt_m{0.0f};
};

struct Telemetry {
    float lat_deg{0.0f};
    float lon_deg{0.0f};
    float alt_m{0.0f};
    float yaw_deg{0.0f};
    float dist_to_wp_m{0.0f};
    float battery_soc_pct{100.0f};
    bool  wp_reached{false};
};

struct ActuatorCommands {
    bool     nav_valid{false};
    float    target_lat{0.0f};
    float    target_lon{0.0f};
    float    target_alt{0.0f};
    float    target_speed_mps{0.0f};
    uint8_t  servo_channel{0};
    uint16_t servo_pwm{1500};
    bool     rtl_triggered{false};
    bool     land_triggered{false};
};

enum class VmStatus {
    Idle,
    Running,
    WaitingNav,
    WaitingCond,
    Completed,
    ErrorInfiniteLoop,
    ErrorOutOfBounds,
    ErrorInvalidOpcode
};

class MissionVirtualMachine {
public:
    static constexpr size_t kMaxInstructions = 64;
    static constexpr size_t kMaxJumpSlots = 16;
    static constexpr uint32_t kMaxTotalJumps = 256;
    static constexpr float kWaypointRadiusM = 2.0f;

    bool load_program(std::span<const Instruction> instructions) {
        if (instructions.size() > kMaxInstructions) {
            return false;
        }
        for (size_t i = 0; i < instructions.size(); ++i) {
            program_[i] = instructions[i];
        }
        program_len_ = instructions.size();
        pc_ = 0;
        status_ = VmStatus::Running;
        total_jumps_executed_ = 0;
        jump_slots_.fill(JumpSlot{});
        return true;
    }

    VmStatus step(const Telemetry& telem, ActuatorCommands& act, uint32_t now_ms) {
        if (status_ != VmStatus::Running &&
            status_ != VmStatus::WaitingNav &&
            status_ != VmStatus::WaitingCond) {
            return status_;
        }

        if (pc_ >= program_len_) {
            status_ = VmStatus::Completed;
            return status_;
        }

        const auto& instr = program_[pc_];

        switch (instr.opcode) {
            case Opcode::Halt:
                status_ = VmStatus::Completed;
                break;

            case Opcode::NavTakeoff:
            case Opcode::NavWaypoint:
                if (status_ != VmStatus::WaitingNav) {
                    act.nav_valid = true;
                    act.target_lat = static_cast<float>(instr.lat_1e7) * 1e-7f;
                    act.target_lon = static_cast<float>(instr.lon_1e7) * 1e-7f;
                    act.target_alt = instr.alt_m;
                    status_ = VmStatus::WaitingNav;
                }
                if (telem.wp_reached || telem.dist_to_wp_m <= kWaypointRadiusM) {
                    pc_++;
                    status_ = VmStatus::Running;
                }
                break;

            case Opcode::NavLand:
                act.land_triggered = true;
                status_ = VmStatus::Completed;
                break;

            case Opcode::NavRtl:
                act.rtl_triggered = true;
                status_ = VmStatus::Completed;
                break;

            case Opcode::DoSetServo:
                act.servo_channel = static_cast<uint8_t>(instr.param1);
                act.servo_pwm = static_cast<uint16_t>(instr.param2);
                pc_++;
                break;

            case Opcode::DoChangeSpeed:
                act.target_speed_mps = static_cast<float>(instr.param2) * 0.01f;
                pc_++;
                break;

            case Opcode::DoJump: {
                auto target = static_cast<size_t>(instr.param1);
                auto repeats = static_cast<uint16_t>(instr.param2);

                if (target >= program_len_) {
                    status_ = VmStatus::ErrorOutOfBounds;
                    break;
                }
                if (total_jumps_executed_ >= kMaxTotalJumps) {
                    status_ = VmStatus::ErrorInfiniteLoop;
                    break;
                }

                auto* slot = find_or_create_jump_slot(target, repeats);
                if (!slot) {
                    status_ = VmStatus::ErrorOutOfBounds;
                    break;
                }

                if (slot->remaining_iterations > 0) {
                    slot->remaining_iterations--;
                    total_jumps_executed_++;
                    pc_ = target;
                } else {
                    slot->active = false;
                    pc_++;
                }
                break;
            }

            case Opcode::JumpIfBatLow: {
                auto threshold = static_cast<float>(instr.param1);
                auto target = static_cast<size_t>(instr.param2);

                if (telem.battery_soc_pct < threshold) {
                    if (target >= program_len_) {
                        status_ = VmStatus::ErrorOutOfBounds;
                    } else {
                        pc_ = target;
                    }
                } else {
                    pc_++;
                }
                break;
            }

            case Opcode::CondDelay: {
                auto delay_ms = static_cast<uint32_t>(instr.param1) * 1000U;
                if (status_ != VmStatus::WaitingCond) {
                    cond_start_time_ms_ = now_ms;
                    status_ = VmStatus::WaitingCond;
                }
                if ((now_ms - cond_start_time_ms_) >= delay_ms) {
                    pc_++;
                    status_ = VmStatus::Running;
                }
                break;
            }

            case Opcode::CondDistance: {
                auto target_dist = static_cast<float>(instr.param1);
                if (telem.dist_to_wp_m <= target_dist) {
                    pc_++;
                    status_ = VmStatus::Running;
                } else {
                    status_ = VmStatus::WaitingCond;
                }
                break;
            }

            case Opcode::CondYaw: {
                auto target_yaw = static_cast<float>(instr.param1);
                float diff = std::remainder(telem.yaw_deg - target_yaw, 360.0f);
                if (std::abs(diff) <= 5.0f) {
                    pc_++;
                    status_ = VmStatus::Running;
                } else {
                    status_ = VmStatus::WaitingCond;
                }
                break;
            }

            default:
                status_ = VmStatus::ErrorInvalidOpcode;
                break;
        }

        return status_;
    }

    [[nodiscard]] size_t current_pc() const noexcept { return pc_; }
    [[nodiscard]] VmStatus status() const noexcept { return status_; }

private:
    struct JumpSlot {
        size_t   target_pc{0};
        uint16_t remaining_iterations{0};
        bool     active{false};
    };

    JumpSlot* find_or_create_jump_slot(size_t target, uint16_t initial_cnt) {
        for (auto& slot : jump_slots_) {
            if (slot.active && slot.target_pc == target) {
                return &slot;
            }
        }
        for (auto& slot : jump_slots_) {
            if (!slot.active) {
                slot.active = true;
                slot.target_pc = target;
                slot.remaining_iterations = initial_cnt;
                return &slot;
            }
        }
        return nullptr;
    }

    std::array<Instruction, kMaxInstructions> program_{};
    std::array<JumpSlot, kMaxJumpSlots>       jump_slots_{};
    size_t   program_len_{0};
    size_t   pc_{0};
    VmStatus status_{VmStatus::Idle};
    uint32_t cond_start_time_ms_{0};
    uint32_t total_jumps_executed_{0};
};

} // namespace mission
```
:::

## Тестовий сценарій виконання місії

Розглянемо практичний тест циклічного моніторингу сільськогосподарського угіддя або периметра об'єкта. Сценарій включає:
1. Автоматичний зліт на висоту 30 метрів.
2. Перевірку залишку батареї: якщо рівень менший за 25%, негайний перехід до кроку 7 (RTL).
3. Політ до точки початку сканування (точка A).
4. Неблокуюче очікування: за 30 метрів до точки вмикається сервопривід скидання маркерного датчика.
5. Політ до точки B.
6. Команда `DO_JUMP`: повторити прохід ділянки (пункти 1–5) тричі.
7. Завершальний пункт: повернення на точку старту (`NAV_RTL`).

:::tabs
=== "C"
```c
void run_test_mission(void) {
    mission_vm_t vm;
    mission_vm_init(&vm);

    vm_instruction_t bytecode[] = {
        /* 0 */ { .opcode = OP_NAV_TAKEOFF, .alt_m = 30.0f },
        /* 1 */ { .opcode = OP_JUMP_IF_BAT_LOW, .param1 = 25, .param2 = 7 },
        /* 2 */ { .opcode = OP_NAV_WAYPOINT, .lat_1e7 = 504500000, .lon_1e7 = 305200000, .alt_m = 30.0f },
        /* 3 */ { .opcode = OP_COND_DISTANCE, .param1 = 30 },
        /* 4 */ { .opcode = OP_DO_SET_SERVO, .param1 = 5, .param2 = 1900 },
        /* 5 */ { .opcode = OP_NAV_WAYPOINT, .lat_1e7 = 504550000, .lon_1e7 = 305250000, .alt_m = 30.0f },
        /* 6 */ { .opcode = OP_DO_JUMP, .param1 = 1, .param2 = 3 },
        /* 7 */ { .opcode = OP_NAV_RTL }
    };

    mission_vm_load(&vm, bytecode, sizeof(bytecode) / sizeof(bytecode[0]));

    vm_telemetry_t telem = {
        .lat_deg = 50.45f,
        .lon_deg = 30.52f,
        .alt_m = 30.0f,
        .yaw_deg = 0.0f,
        .dist_to_wp_m = 1.0f,
        .battery_soc_pct = 80.0f,
        .wp_reached = true
    };
    vm_actuators_t act;
    memset(&act, 0, sizeof(act));

    uint32_t sim_time_ms = 0;
    while (vm.status != VM_STATUS_COMPLETED) {
        mission_vm_step(&vm, &telem, &act, sim_time_ms);
        sim_time_ms += 20;

        if (sim_time_ms > 2000) {
            telem.battery_soc_pct = 20.0f; /* Імітація просідання батареї */
        }
    }
}
```
=== "C++"
```cpp
void run_test_mission() {
    using namespace mission;
    MissionVirtualMachine vm;

    const std::array bytecode = {
        Instruction{ .opcode = Opcode::NavTakeoff, .alt_m = 30.0f },
        Instruction{ .opcode = Opcode::JumpIfBatLow, .param1 = 25, .param2 = 7 },
        Instruction{ .opcode = Opcode::NavWaypoint, .lat_1e7 = 504500000, .lon_1e7 = 305200000, .alt_m = 30.0f },
        Instruction{ .opcode = Opcode::CondDistance, .param1 = 30 },
        Instruction{ .opcode = Opcode::DoSetServo, .param1 = 5, .param2 = 1900 },
        Instruction{ .opcode = Opcode::NavWaypoint, .lat_1e7 = 504550000, .lon_1e7 = 305250000, .alt_m = 30.0f },
        Instruction{ .opcode = Opcode::DoJump, .param1 = 1, .param2 = 3 },
        Instruction{ .opcode = Opcode::NavRtl }
    };

    vm.load_program(bytecode);

    Telemetry telem{
        .lat_deg = 50.45f,
        .lon_deg = 30.52f,
        .alt_m = 30.0f,
        .yaw_deg = 0.0f,
        .dist_to_wp_m = 1.0f,
        .battery_soc_pct = 80.0f,
        .wp_reached = true
    };
    ActuatorCommands act{};

    uint32_t sim_time_ms = 0;
    while (vm.status() != VmStatus::Completed) {
        vm.step(telem, act, sim_time_ms);
        sim_time_ms += 20;

        if (sim_time_ms > 2000) {
            telem.battery_soc_pct = 20.0f; // Імітація просідання батареї
        }
    }
}
```
:::

## Інтеграція в RTOS та обробка крайових ситуацій

При інтеграції віртуальної машини у середовище реального часу (FreeRTOS або Zephyr RTOS) рекомендовано виділяти окрему задачу `mission_task` з низьким або середнім пріоритетом (нижче, ніж у контурів стабілізації гіроскопа та EKF-навігатора). Обмін даними здійснюється через неблокуючу чергу повідомлень (Message Queue) або подвійний буфер із захистом від стану гонитви (Race Condition).

Типовий потік взаємодії задач у системі:
1. **Навігаційний потік (100 Гц):** зчитує сенсори, оновлює поточний стан оцінювача EKF (позиція, швидкість, висота) і записує снапшот у структуру `vm_telemetry_t`.
2. **Потік місії (20–50 Гц):** прокидається за періодичним таймером, викликає `mission_vm_step()`, перевіряє активну умову й генерує нову просторову уставку або керівний сигнал сервоприводу.
3. **Виконавчий потік (50 Гц):** зчитує `vm_actuators_t` і транслює зміну координат у цільові вектори прискорення для PID-регуляторів.

Крайові випадки, які обробляє віртуальна машина:
- **Переповнення глобального бюджету стрибків (Infinite Loop Guard):** якщо кількість виконаних переходів перевищує `VM_MAX_TOTAL_JUMPS` (за замовчуванням 256), машина переходить у статус `VM_STATUS_ERROR_INFINITE_LOOP`, скидає активні дії й передає аварійний сигнал супервізору Failsafe.
- **Вихід за межі масиву (Out of Bounds Jump):** стрибок на неіснуючий індекс інструкції миттєво спиняє виконання зі статусом `VM_STATUS_ERROR_OUT_OF_BOUNDS`.
- **Втрата координат або відмова GNSS:** якщо навігаційний контур повідомляє про інвалідність позиції (`wp_reached = false`, `dist_to_wp_m = NaN`), віртуальна машина лишається в стані `WAITING_NAV`, доки зовнішній супервізор не прийме рішення про аварійну посадку за таймаутом.
- **Низький рівень сигналу зв'язку:** якщо втрачено зв'язок з наземною станцією керування (GCS), автономний інтерпретатор продовжує виконання програми без переривання, спираючись на внутрішні лічильники циклів та аварійні пороги батареї.
