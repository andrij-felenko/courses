#include <cstdint>
#include <span>

class RdcTransceiver {
public:
    struct Telemetry {
        float position_deg;   // Кут у градусах (0.0 .. 360.0)
        float velocity_rpm;   // Швидкість обертання у прох/хв
        uint8_t fault_code;   // Байт помилок (0 = норма)
        bool has_error;
    };

    explicit RdcTransceiver(void* spi_handle) : m_spi_handle(spi_handle) {}

    Telemetry update() {
        Telemetry result{};
        uint16_t raw_pos = read_register(0x80);
        uint16_t raw_vel = read_register(0x82);
        uint8_t fault = static_cast<uint8_t>(read_register(0xFF) & 0xFF);

        // Перетворення 16-бітного коду в градуси: (raw / 65536) * 360.0
        result.position_deg = (static_cast<float>(raw_pos) / 65536.0f) * 360.0f;
        
        // Перетворення коду швидкості у RPM (залежно від масштабу RDC)
        int16_t signed_vel = static_cast<int16_t>(raw_vel);
        result.velocity_rpm = (static_cast<float>(signed_vel) / 32768.0f) * 6000.0f;

        result.fault_code = fault;
        result.has_error = (fault != 0);

        return result;
    }

private:
    void* m_spi_handle;

    uint16_t read_register(uint8_t reg) {
        uint8_t tx[3] = { reg, 0x00, 0x00 };
        uint8_t rx[3] = { 0 };
        spi_transfer_hardware(m_spi_handle, tx, rx, 3);
        return (static_cast<uint16_t>(rx[1]) << 8) | rx[2];
    }

    extern "C" void spi_transfer_hardware(void* handle, const uint8_t* tx, uint8_t* rx, uint16_t len);
};
