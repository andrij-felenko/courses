#include <cstdint>
#include <array>
#include <atomic>
#include <mutex>
#include <optional>

template <size_t MaxActuators = 16>
class ThreadSafeActuatorConflator {
public:
    struct Command {
        uint64_t sequence_num{0};
        float target_value{0.0f};
        uint32_t timestamp_ms{0};
    };

    bool push(uint32_t actuator_id, float value, uint64_t seq_num, uint32_t now_ms) {
        if (actuator_id >= MaxActuators) return false;

        std::lock_guard<std::mutex> lock(mutexes_[actuator_id]);

        // Відсіювання застарілих команд (out-of-order)
        if (seq_num <= last_processed_seq_[actuator_id]) {
            suppressed_count_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        if (slots_occupied_[actuator_id]) {
            if (seq_num <= slots_[actuator_id].sequence_num) {
                suppressed_count_.fetch_add(1, std::memory_order_relaxed);
                return false;
            }
            // Згортання застарілої непоширеної устави в слоті
            suppressed_count_.fetch_add(1, std::memory_order_relaxed);
        }

        slots_[actuator_id] = Command{seq_num, value, now_ms};
        slots_occupied_[actuator_id] = true;
        return true;
    }

    std::optional<Command> pop(uint32_t actuator_id) {
        if (actuator_id >= MaxActuators) return std::nullopt;

        std::lock_guard<std::mutex> lock(mutexes_[actuator_id]);

        if (!slots_occupied_[actuator_id]) {
            return std::nullopt;
        }

        Command cmd = slots_[actuator_id];
        last_processed_seq_[actuator_id] = cmd.sequence_num;
        slots_occupied_[actuator_id] = false;
        return cmd;
    }

    [[nodiscard]] uint32_t get_suppressed_count() const noexcept {
        return suppressed_count_.load(std::memory_order_relaxed);
    }

private:
    std::array<std::mutex, MaxActuators> mutexes_{};
    std::array<Command, MaxActuators> slots_{};
    std::array<bool, MaxActuators> slots_occupied_{};
    std::array<uint64_t, MaxActuators> last_processed_seq_{};
    std::atomic<uint32_t> suppressed_count_{0};
};
