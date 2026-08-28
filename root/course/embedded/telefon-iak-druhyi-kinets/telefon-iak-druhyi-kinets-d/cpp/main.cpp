#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <functional>
#include <optional>

/* Типізована бінарна структура кадру телеметрії */
struct alignas(1) TelemetryPayload {
    int16_t  temperature_centi_c{0};
    uint16_t battery_voltage_mv{0};
    uint32_t sequence_number{0};
};
static_assert(sizeof(TelemetryPayload) == 8, "TelemetryPayload must be exactly 8 bytes packed");

/* Перелік підтримуваних команд керування */
enum class DeviceCommand : uint8_t {
    ResetSequenceNumber = 0x01,
    SetSamplingInterval = 0x02,
    CalibrateSensors    = 0x03,
};

class BleTelemetryServer {
public:
    using CommandHandler = std::function<void(DeviceCommand, std::span<const uint8_t>)>;

    explicit BleTelemetryServer(CommandHandler cmd_handler = nullptr)
        : cmd_handler_{std::move(cmd_handler)} {}

    void on_connected(uint16_t conn_handle, uint16_t initial_mtu = 23) noexcept {
        conn_handle_ = conn_handle;
        negotiated_mtu_ = initial_mtu;
        notifications_enabled_ = false;
        is_connected_ = true;
    }

    void on_disconnected() noexcept {
        conn_handle_ = kInvalidHandle;
        notifications_enabled_ = false;
        is_connected_ = false;
        negotiated_mtu_ = kDefaultMtu;
    }

    void on_mtu_updated(uint16_t new_mtu) noexcept {
        negotiated_mtu_ = new_mtu;
    }

    /* Обробка запиту на зчитування телеметрії */
    [[nodiscard]] std::span<const uint8_t> handle_read_telemetry() const noexcept {
        return std::span<const uint8_t>{
            reinterpret_cast<const uint8_t*>(&latest_payload_),
            sizeof(TelemetryPayload)
        };
    }

    /* Обробка запису в дескриптор CCCD */
    [[nodiscard]] bool handle_write_cccd(std::span<const uint8_t> data) noexcept {
        if (data.size() != 2) {
            return false;
        }
        const uint16_t cccd_flags = static_cast<uint16_t>(data[0]) |
                                   (static_cast<uint16_t>(data[1]) << 8);
        notifications_enabled_ = (cccd_flags & kCccdNotificationBit) != 0;
        return true;
    }

    /* Обробка вхідної команди */
    [[nodiscard]] bool handle_write_command(std::span<const uint8_t> data) {
        if (data.empty()) {
            return false;
        }

        const auto cmd = static_cast<DeviceCommand>(data[0]);
        const auto payload = data.subspan(1);

        if (cmd == DeviceCommand::ResetSequenceNumber) {
            latest_payload_.sequence_number = 0;
        }

        if (cmd_handler_) {
            cmd_handler_(cmd, payload);
        }
        return true;
    }

    /* Формування та відправка асинхронного сповіщення */
    [[nodiscard]] std::optional<std::span<const uint8_t>> prepare_notification(int16_t temp_c, uint16_t vbatt_mv) noexcept {
        if (!is_connected_ || !notifications_enabled_) {
            return std::nullopt;
        }

        if (sizeof(TelemetryPayload) > static_cast<size_t>(negotiated_mtu_ - kAttHeaderSize)) {
            return std::nullopt; // Пакет перевищує поточний узгоджений MTU
        }

        latest_payload_.temperature_centi_c = temp_c;
        latest_payload_.battery_voltage_mv = vbatt_mv;
        ++latest_payload_.sequence_number;

        return std::span<const uint8_t>{
            reinterpret_cast<const uint8_t*>(&latest_payload_),
            sizeof(TelemetryPayload)
        };
    }

    [[nodiscard]] bool is_ready_to_notify() const noexcept {
        return is_connected_ && notifications_enabled_;
    }

    [[nodiscard]] uint16_t current_mtu() const noexcept { return negotiated_mtu_; }

private:
    static constexpr uint16_t kInvalidHandle = 0xFFFF;
    static constexpr uint16_t kDefaultMtu = 23;
    static constexpr uint16_t kAttHeaderSize = 3;
    static constexpr uint16_t kCccdNotificationBit = 0x0001;

    uint16_t conn_handle_{kInvalidHandle};
    uint16_t negotiated_mtu_{kDefaultMtu};
    bool notifications_enabled_{false};
    bool is_connected_{false};

    TelemetryPayload latest_payload_{};
    CommandHandler cmd_handler_{};
};
