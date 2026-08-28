#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <chrono>
#include <cstring>
#include <cstdint>
#include <expected>
#include <system_error>

// Двійкова структура кадру польотної телеметрії (фіксований розмір 32 байти)
#pragma pack(push, 1)
struct FlightTelemetryFrame {
    uint32_t timestamp_ms; // Час від старту контролера
    float roll_deg;        // Крен (-180.0 .. +180.0)
    float pitch_deg;       // Тангаж (-90.0 .. +90.0)
    float yaw_deg;         // Рискання (0.0 .. 360.0)
    float altitude_m;      // Висота барометрична/GPS
    float battery_voltage; // Напруга акумулятора (В)
    uint8_t arm_state;     // 0 = Disarmed, 1 = Armed
    uint8_t flight_mode;   // 0 = Manual, 1 = AltHold, 2 = Auto, 3 = RTL
    uint16_t crc16;        // Контрольна сума CRC-16-CCITT
};
#pragma pack(pop)

// Інтерфейс сокета DataChannel (RAII-абстракція над SCTP/DTLS тунелем)
class DataChannelSession {
public:
    virtual ~DataChannelSession() = default;
    virtual bool is_open() const noexcept = 0;
    virtual size_t buffered_amount() const noexcept = 0;
    virtual std::expected<void, std::error_code> send(std::span<const std::byte> data) = 0;
};

// Контролер відправки високочастотної телеметрії
class TelemetryBroadcaster {
public:
    explicit TelemetryBroadcaster(std::shared_ptr<DataChannelSession> channel)
        : channel_(std::move(channel)) {}

    // Обчислення простої контрольної суми CRC-16 для захисту цілісності
    static uint16_t compute_crc16(std::span<const std::byte> bytes) noexcept {
        uint16_t crc = 0xFFFF;
        for (std::byte b : bytes) {
            crc ^= static_cast<uint8_t>(b);
            for (int i = 0; i < 8; ++i) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0x8408; // Поліном CCITT reverse
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }

    // Відправка одного телеметричного кадру з контролем черги сокета (Backpressure)
    std::expected<void, std::string> broadcast_frame(float roll, float pitch, float yaw,
                                                    float alt, float vbat, uint8_t mode) {
        if (!channel_ || !channel_->is_open()) {
            return std::unexpected("Канал зв'язку DataChannel не відкритий");
        }

        // Захист від переповнення системного буфера SCTP (Backpressure)
        // Якщо в буфері відправки вже накопичилося понад 64 КіБ, скидаємо застарілий кадр
        if (channel_->buffered_amount() > 65536) {
            return std::unexpected("Черга відправки переповнена: кадр телеметрії пропущено");
        }

        auto now = std::chrono::steady_clock::now();
        uint32_t now_ms = static_cast<uint32_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count()
        );

        FlightTelemetryFrame frame{
            .timestamp_ms = now_ms,
            .roll_deg = roll,
            .pitch_deg = pitch,
            .yaw_deg = yaw,
            .altitude_m = alt,
            .battery_voltage = vbat,
            .arm_state = 1,
            .flight_mode = mode,
            .crc16 = 0
        };

        // Обчислюємо CRC-16 від усіх полів крім самого поля crc16
        auto payload_bytes = std::as_bytes(std::span{&frame, 1});
        auto data_to_hash = payload_bytes.subspan(0, sizeof(FlightTelemetryFrame) - sizeof(uint16_t));
        frame.crc16 = compute_crc16(data_to_hash);

        // Відправляємо бінарний буфер через SCTP без блокування
        auto result = channel_->send(payload_bytes);
        if (!result) {
            return std::unexpected("Помилка сокета при надсиланні кадру");
        }

        return {};
    }

private:
    std::shared_ptr<DataChannelSession> channel_;
};
