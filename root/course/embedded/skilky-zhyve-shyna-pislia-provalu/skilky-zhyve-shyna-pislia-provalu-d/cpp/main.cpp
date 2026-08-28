#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <optional>
#include <concepts>
#include <bit>

// ── C++20 Type-Safe Power Loss Protection Architecture ─────────────────────

enum class PowerFaultReason : uint8_t {
    InvalidMagic,
    ChecksumMismatch,
    FlashWriteFailure,
    EmptyBuffer
};

struct alignas(8) EmergencyPayload {
    uint32_t sequence_id{0};
    uint32_t uptime_seconds{0};
    int32_t  actuator_position{0};
    float    calibrated_offset{0.0f};
    uint32_t error_flags{0};
};

struct alignas(8) StoredRecord {
    static constexpr uint32_t ValidMagic = 0x504C5031U; // 'PLP1'

    uint32_t magic{0};
    EmergencyPayload payload{};
    uint32_t checksum{0};
    uint32_t padding{0};
};

static_assert(sizeof(StoredRecord) % 8 == 0, "Flash writes require 64-bit alignment");

// Концепт драйвера енергонезалежної пам'яті
template <typename T>
concept StorageDevice = requires(T dev, uint32_t addr, std::span<const uint64_t> data) {
    { dev.write_double_words(addr, data) } -> std::same_as<bool>;
    { dev.read_span(addr) } -> std::same_as<std::span<const uint8_t>>;
};

class PowerLossManager {
public:
    constexpr explicit PowerLossManager(uint32_t flash_addr) noexcept 
        : base_addr_(flash_addr) {}

    // Обробник аварійного відключення (викликається в NMI)
    template <StorageDevice Storage>
    void handle_power_failure(Storage& storage, const EmergencyPayload& live_data) noexcept {
        // 1. Апаратне скидання споживання (Load Shedding)
        emergency_shed_loads();

        // 2. Підготовка запису
        StoredRecord record{
            .magic = StoredRecord::ValidMagic,
            .payload = live_data,
            .checksum = calculate_crc32(std::as_bytes(std::span{&live_data, 1})),
            .padding = 0xAA55AA55U
        };
        record.payload.sequence_id++;

        // 3. Запис тіла даних (без поля magic для атомарності)
        auto raw_words = std::span<const uint64_t>(
            reinterpret_cast<const uint64_t*>(&record),
            sizeof(StoredRecord) / sizeof(uint64_t)
        );

        // Пишемо хвіст запису
        if (storage.write_double_words(base_addr_ + 8, raw_words.subspan(1))) {
            // Пишемо заголовок із Magic останнім
            storage.write_double_words(base_addr_, raw_words.first(1));
        }

        // 4. Безпечний сон процесора до спрацювання Brown-Out Reset
        enter_safe_parking();
    }

    // Відновлення стану під час старту без використання винятків
    template <StorageDevice Storage>
    [[nodiscard]] std::expected<EmergencyPayload, PowerFaultReason> 
    restore_on_boot(const Storage& storage) const noexcept {
        auto mem_view = storage.read_span(base_addr_);
        if (mem_view.size() < sizeof(StoredRecord)) {
            return std::unexpected(PowerFaultReason::EmptyBuffer);
        }

        const auto* stored = reinterpret_cast<const StoredRecord*>(mem_view.data());

        if (stored->magic != StoredRecord::ValidMagic) {
            return std::unexpected(PowerFaultReason::InvalidMagic);
        }

        const uint32_t expected_crc = calculate_crc32(
            std::as_bytes(std::span{&stored->payload, 1})
        );

        if (stored->checksum != expected_crc) {
            return std::unexpected(PowerFaultReason::ChecksumMismatch);
        }

        return stored->payload;
    }

private:
    uint32_t base_addr_;

    static void emergency_shed_loads() noexcept {
        // Прямий запис у регістри керування GPIO для вимкнення ключів
        // GPIOB->BSRR = GPIO_PIN_0; // SHED_EN = 0
    }

    static void enter_safe_parking() noexcept {
        while (true) {
            #if defined(__arm__) || defined(__thumb__)
            asm volatile("wfi");
            #endif
        }
    }

    static uint32_t calculate_crc32(std::span<const std::byte> bytes) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (auto b : bytes) {
            crc ^= static_cast<uint8_t>(b);
            for (int i = 0; i < 8; ++i) {
                crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
            }
        }
        return ~crc;
    }
};
