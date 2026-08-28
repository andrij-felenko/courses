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
