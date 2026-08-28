#include <cstdint>
#include <cstddef>
#include <expected>
#include <span>
#include <functional>

/* Системні коди помилок у стилі C++23 */
enum class SensorStatus : uint8_t {
    Ok,
    CommunicationError,
    InvalidDevice,
    Timeout,
    InvalidParameter
};

/* Системна структура виміряних величин */
struct EnvironmentReading {
    float temperature_celsius;
    float pressure_hpa;
};

/* Чистий C++ інтерфейс апаратної шини */
class II2cBus {
public:
    virtual ~II2cBus() = default;
    virtual bool read_registers(uint8_t dev_addr, uint8_t reg, std::span<uint8_t> buffer) = 0;
    virtual bool write_registers(uint8_t dev_addr, uint8_t reg, std::span<const uint8_t> buffer) = 0;
};

/* Зовнішній C-інтерфейс вендорського SDK */
extern "C" {
    typedef int8_t (*vendor_read_fn)(uint8_t reg_addr, uint8_t *data, uint32_t len, void *intf_ptr);
    typedef int8_t (*vendor_write_fn)(uint8_t reg_addr, const uint8_t *data, uint32_t len, void *intf_ptr);
    typedef void (*vendor_delay_us_fn)(uint32_t period_us, void *intf_ptr);

    struct vendor_sensor_dev_t {
        uint8_t chip_id;
        void *intf_ptr;
        vendor_read_fn read;
        vendor_write_fn write;
        vendor_delay_us_fn delay_us;
    };
}
