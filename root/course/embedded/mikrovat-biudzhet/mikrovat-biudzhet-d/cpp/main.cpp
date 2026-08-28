#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <concepts>

namespace intermittent {

constexpr uint32_t SignatureValid = 0x5AA5C33C;
constexpr size_t MaxSensorAxes = 4;

struct alignas(4) CheckpointData {
    uint32_t signature{0};
    uint8_t  current_task_id{0};
    uint8_t  transaction_epoch{0};
    uint16_t checksum{0};
    std::array<int32_t, MaxSensorAxes> sensor_raw_data{};
    float calculated_vibration_rms{0.0F};
    bool  radio_packet_sent{false};

    [[nodiscard]] constexpr uint16_t compute_crc() const noexcept {
        const auto* raw = reinterpret_cast<const uint8_t*>(this);
        constexpr size_t payload_len = sizeof(CheckpointData) - sizeof(uint16_t);
        uint16_t crc = 0xFFFF;
        for (size_t i = 0; i < payload_len; ++i) {
            crc ^= static_cast<uint16_t>(raw[i]) << 8;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc & 0x8000) ? static_cast<uint16_t>((crc << 1) ^ 0x1021)
                                     : static_cast<uint16_t>(crc << 1);
            }
        }
        return crc;
    }

    [[nodiscard]] bool is_valid() const noexcept {
        return (signature == SignatureValid) && (checksum == compute_crc());
    }

    void finalize_and_seal(uint8_t next_task) noexcept {
        signature = SignatureValid;
        current_task_id = next_task;
        transaction_epoch++;
        checksum = compute_crc();
    }
};

class IntermittentExecutor {
public:
    explicit IntermittentExecutor(CheckpointData& slot_a, CheckpointData& slot_b, uint8_t& active_flag) noexcept
        : slots_{slot_a, slot_b}, active_index_{active_flag} {
        ensure_valid_state();
    }

    void run_step() noexcept {
        auto& active = get_active();
        auto& shadow = get_shadow();

        // Клонування верифікованого стану в робочий тіньовий буфер
        shadow = active;

        switch (active.current_task_id) {
            case 0:
                if (execute_task_sample(shadow)) {
                    commit_transaction(1);
                }
                break;
            case 1:
                if (execute_task_dsp(shadow)) {
                    commit_transaction(2);
                }
                break;
            case 2:
                if (execute_task_transmit(shadow)) {
                    commit_transaction(3);
                }
                break;
            case 3:
                commit_transaction(0);
                break;
            default:
                commit_transaction(0);
                break;
        }
    }

    [[nodiscard]] uint8_t current_task() const noexcept {
        return get_active().current_task_id;
    }

private:
    std::array<std::reference_wrapper<CheckpointData>, 2> slots_;
    uint8_t& active_index_;

    [[nodiscard]] CheckpointData& get_active() noexcept {
        return slots_[active_index_ & 1].get();
    }

    [[nodiscard]] const CheckpointData& get_active() const noexcept {
        return slots_[active_index_ & 1].get();
    }

    [[nodiscard]] CheckpointData& get_shadow() noexcept {
        return slots_[(active_index_ ^ 1) & 1].get();
    }

    void commit_transaction(uint8_t next_task_id) noexcept {
        auto& shadow = get_shadow();
        shadow.finalize_and_seal(next_task_id);
        // Атомарна зміна індексу активного буфера у FRAM
        active_index_ ^= 1;
    }

    void ensure_valid_state() noexcept {
        if (!get_active().is_valid()) {
            auto& active = get_active();
            active = CheckpointData{};
            active.finalize_and_seal(0);
        }
    }

    static bool execute_task_sample(CheckpointData& work) noexcept {
        work.sensor_raw_data = {1204, -450, 8900, 34};
        return true;
    }

    static bool execute_task_dsp(CheckpointData& work) noexcept {
        int64_t sum_squares = 0;
        for (size_t i = 0; i < 3; ++i) {
            sum_squares += static_cast<int64_t>(work.sensor_raw_data[i]) * work.sensor_raw_data[i];
        }
        work.calculated_vibration_rms = static_cast<float>(sum_squares / 10000);
        return true;
    }

    static bool execute_task_transmit(CheckpointData& work) noexcept {
        work.radio_packet_sent = true;
        return true;
    }
};

} // namespace intermittent
