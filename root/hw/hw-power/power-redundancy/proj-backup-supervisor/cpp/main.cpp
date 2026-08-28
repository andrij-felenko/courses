#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>
#include <optional>

namespace EmbeddedPower {

inline constexpr uint32_t MagicHeaderValue = 0x504F5752; // "POWR"
inline constexpr uint16_t SlotAddressA = 0x0100;
inline constexpr uint16_t SlotAddressB = 0x0200;

enum class MemoryOpcode : uint8_t {
    WriteEnable  = 0x06,
    WritePayload = 0x02,
    ReadPayload  = 0x03
};

struct [[gnu::packed]] SystemSnapshotRecord {
    uint32_t magic{MagicHeaderValue};
    uint64_t sequence_id{0};
    uint64_t timestamp_ms{0};
    int32_t  actuator_position_steps{0};
    int16_t  calibrated_zero_offset{0};
    float    last_bus_voltage{0.0f};
    float    ambient_temperature{0.0f};
    uint8_t  system_state_flags{0};
    uint8_t  reserved_padding[3]{0, 0, 0};
    uint32_t crc32{0};

    [[nodiscard]] std::span<const uint8_t> payload_span() const noexcept {
        constexpr size_t payload_size = sizeof(SystemSnapshotRecord) - sizeof(uint32_t);
        return {reinterpret_cast<const uint8_t*>(this), payload_size};
    }
};

template <typename SpiBus>
concept SpiInterface = requires(SpiBus spi, std::span<const uint8_t> out_data, std::span<uint8_t> in_data) {
    { spi.chip_select() } -> std::same_as<void>;
    { spi.chip_deselect() } -> std::same_as<void>;
    { spi.write_blocking(out_data) } -> std::same_as<void>;
    { spi.read_blocking(in_data) } -> std::same_as<void>;
};

template <SpiInterface SpiDriver>
class PowerFailSupervisor {
public:
    explicit PowerFailSupervisor(SpiDriver& spi_driver) noexcept : spi_(spi_driver) {}

    void process_dying_gasp(int32_t current_actuator_pos, float bus_volts, float temp_c, uint64_t uptime) noexcept {
        if (is_dying_gasp_active_) {
            return;
        }
        is_dying_gasp_active_ = true;

        SystemSnapshotRecord record{
            .magic = MagicHeaderValue,
            .sequence_id = ++last_sequence_counter_,
            .timestamp_ms = uptime,
            .actuator_position_steps = current_actuator_pos,
            .calibrated_zero_offset = -12,
            .last_bus_voltage = bus_volts,
            .ambient_temperature = temp_c,
            .system_state_flags = 0x81,
            .reserved_padding = {0, 0, 0},
            .crc32 = 0
        };

        record.crc32 = compute_crc32_fast(record.payload_span());

        const uint16_t target_addr = (record.sequence_id & 1ULL) ? SlotAddressA : SlotAddressB;
        write_record_to_fram(target_addr, record);
    }

    [[nodiscard]] std::optional<SystemSnapshotRecord> restore_latest_snapshot() noexcept {
        const auto record_a = read_record_from_fram(SlotAddressA);
        const auto record_b = read_record_from_fram(SlotAddressB);

        const bool valid_a = record_a && is_record_valid(*record_a);
        const bool valid_b = record_b && is_record_valid(*record_b);

        if (valid_a && valid_b) {
            return (record_a->sequence_id > record_b->sequence_id) ? record_a : record_b;
        }
        if (valid_a) return record_a;
        if (valid_b) return record_b;

        return std::nullopt;
    }

private:
    SpiDriver& spi_;
    uint64_t last_sequence_counter_{0};
    bool is_dying_gasp_active_{false};

    void execute_write_enable() noexcept {
        const uint8_t cmd = static_cast<uint8_t>(MemoryOpcode::WriteEnable);
        spi_.chip_select();
        spi_.write_blocking(std::span<const uint8_t, 1>(&cmd, 1));
        spi_.chip_deselect();
    }

    void write_record_to_fram(uint16_t address, const SystemSnapshotRecord& record) noexcept {
        execute_write_enable();

        const std::array<uint8_t, 3> header_bytes{
            static_cast<uint8_t>(MemoryOpcode::WritePayload),
            static_cast<uint8_t>(address >> 8),
            static_cast<uint8_t>(address & 0xFF)
        };

        const auto raw_record_span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&record), sizeof(SystemSnapshotRecord)
        );

        spi_.chip_select();
        spi_.write_blocking(header_bytes);
        spi_.write_blocking(raw_record_span);
        spi_.chip_deselect();
    }

    [[nodiscard]] std::optional<SystemSnapshotRecord> read_record_from_fram(uint16_t address) noexcept {
        const std::array<uint8_t, 3> header_bytes{
            static_cast<uint8_t>(MemoryOpcode::ReadPayload),
            static_cast<uint8_t>(address >> 8),
            static_cast<uint8_t>(address & 0xFF)
        };

        SystemSnapshotRecord record{};
        auto raw_record_span = std::span<uint8_t>(
            reinterpret_cast<uint8_t*>(&record), sizeof(SystemSnapshotRecord)
        );

        spi_.chip_select();
        spi_.write_blocking(header_bytes);
        spi_.read_blocking(raw_record_span);
        spi_.chip_deselect();

        return record;
    }

    [[nodiscard]] static bool is_record_valid(const SystemSnapshotRecord& rec) noexcept {
        if (rec.magic != MagicHeaderValue) {
            return false;
        }
        return compute_crc32_fast(rec.payload_span()) == rec.crc32;
    }

    [[nodiscard]] static uint32_t compute_crc32_fast(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFUL;
        for (const uint8_t byte_val : data) {
            crc ^= byte_val;
            for (int bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1)));
            }
        }
        return ~crc;
    }
};

} // namespace EmbeddedPower
