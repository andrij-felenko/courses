#include <cstdint>
#include <array>
#include <span>
#include <algorithm>

namespace mission {

enum class Opcode : uint8_t {
    Halt         = 0,
    Waypoint     = 1,
    Jump         = 2,
    CheckBattery = 3
};

struct Instruction {
    Opcode   opcode{Opcode::Halt};
    uint16_t target{0};
    uint16_t param{0};
    float    lat{0.0f};
    float    lon{0.0f};
    float    alt{0.0f};
};

class SimpleMissionVm {
public:
    static constexpr size_t   kMaxItems = 64;
    static constexpr uint16_t kMaxTotalJumps = 128;

    explicit SimpleMissionVm(std::span<const Instruction> program) {
        const size_t copy_len = std::min(program.size(), kMaxItems);
        for (size_t i = 0; i < copy_len; ++i) {
            code_[i] = program[i];
        }
        code_len_ = copy_len;
        jump_counts_.fill(0);
    }

    void tick(float bat_soc_pct, bool wp_reached) noexcept {
        if (finished_ || error_infinite_loop_ || pc_ >= code_len_) {
            finished_ = true;
            return;
        }

        const auto& curr = code_[pc_];

        switch (curr.opcode) {
            case Opcode::Halt:
                finished_ = true;
                break;

            case Opcode::Waypoint:
                if (wp_reached) {
                    pc_++;
                }
                break;

            case Opcode::CheckBattery:
                if (bat_soc_pct < static_cast<float>(curr.param)) {
                    pc_ = curr.target; // Аварійний перехід
                } else {
                    pc_++;
                }
                break;

            case Opcode::Jump:
                if (total_jumps_ >= kMaxTotalJumps) {
                    error_infinite_loop_ = true;
                    break;
                }

                if (jump_counts_[pc_] < curr.param) {
                    jump_counts_[pc_]++;
                    total_jumps_++;
                    pc_ = curr.target;
                } else {
                    jump_counts_[pc_] = 0; // Скидання лічильника
                    pc_++;
                }
                break;
        }
    }

    [[nodiscard]] bool is_finished() const noexcept { return finished_; }
    [[nodiscard]] bool has_error() const noexcept { return error_infinite_loop_; }
    [[nodiscard]] size_t program_counter() const noexcept { return pc_; }

private:
    std::array<Instruction, kMaxItems> code_{};
    std::array<uint16_t, kMaxItems>    jump_counts_{};
    size_t   code_len_{0};
    size_t   pc_{0};
    uint16_t total_jumps_{0};
    bool     finished_{false};
    bool     error_infinite_loop_{false};
};

} // namespace mission
