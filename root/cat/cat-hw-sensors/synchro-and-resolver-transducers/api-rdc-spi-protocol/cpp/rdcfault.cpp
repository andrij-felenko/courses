#include <cstdint>
#include <utility>

enum class RdcFault : uint8_t {
    None = 0,
    ParityError,
    LossOfSignal,     // LOS
    LossOfTracking,   // LOT
    DegradationSignal // DOS
};

struct RdcData {
    float angle_rad{0.0f};
    float velocity_rad_s{0.0f};
    RdcFault fault{RdcFault::None};
};

class RdcDriver {
public:
    explicit RdcDriver(float max_velocity_rad_s) 
        : max_velocity_(max_velocity_rad_s) {}

    std::pair<RdcData, bool> update() {
        RdcData data{};

        // 1. Формування імпульсу фіксації SAMPLE
        setSamplePin(false);
        delayNs(500);
        setSamplePin(true);

        // 2. Зчитування через SPI
        setCsPin(false);
        delayNs(100);

        const uint16_t pos_frame = spiTransfer16(0x0000);
        const uint16_t vel_status_frame = spiTransfer16(0x0000);

        setCsPin(true);
        delayNs(500);

        // 3. Валідація паритету кадру
        if (!checkParityOdd(pos_frame)) {
            data.fault = RdcFault::ParityError;
            ++parity_errors_;
            return {data, false};
        }

        // 4. Аналіз діагностичних бітів
        const uint8_t flags = static_cast<uint8_t>(vel_status_frame & 0xFF);
        if (flags & (1U << 0)) { // LOS
            data.fault = RdcFault::LossOfSignal;
            return {data, false};
        }
        if (flags & (1U << 2)) { // LOT
            data.fault = RdcFault::LossOfTracking;
            return {data, false};
        }

        // 5. Перетворення значення у кут і швидкість
        const uint16_t raw_pos = (pos_frame >> 1) & 0x7FFF;
        data.angle_rad = (static_cast<float>(raw_pos) / 32768.0f) * 6.28318530718f;

        const int16_t raw_vel = static_cast<int16_t>(vel_status_frame);
        data.velocity_rad_s = (static_cast<float>(raw_vel) / 32767.0f) * max_velocity_;

        if (flags & (1U << 1)) { // DOS
            data.fault = RdcFault::DegradationSignal;
        }

        return {data, true};
    }

    [[nodiscard]] uint32_t getParityErrorCount() const noexcept {
        return parity_errors_;
    }

private:
    float max_velocity_;
    uint32_t parity_errors_{0};

    // Апаратні абстракції периферії
    void setSamplePin(bool state);
    void setCsPin(bool state);
    void delayNs(uint32_t ns);
    uint16_t spiTransfer16(uint16_t data);

    static bool checkParityOdd(uint16_t frame) noexcept {
        frame ^= frame >> 8;
        frame ^= frame >> 4;
        frame ^= frame >> 2;
        frame ^= frame >> 1;
        return (frame & 0x1) != 0;
    }
};
