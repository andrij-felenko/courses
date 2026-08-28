// inc/sensor_service.hpp — Ідіоматичний ізольований драйвер мовою C++
#ifndef SENSOR_SERVICE_HPP
#define SENSOR_SERVICE_HPP

#include <cstdint>
#include <span>
#include <expected>

namespace drivers::sensors {

#if defined(__GNUC__) || defined(__clang__)
    #define PORT_PACKED_STRUCT struct [[gnu::packed]]
    #define PORT_RAM_FUNC      [[gnu::section(".ramfunc"), gnu::noinline]]
#elif defined(__ICCARM__)
    #define PORT_PACKED_STRUCT __packed struct
    #define PORT_RAM_FUNC      __ramfunc
#else
    #define PORT_PACKED_STRUCT struct
    #define PORT_RAM_FUNC
#endif

PORT_PACKED_STRUCT SensorDataPacket {
    std::uint32_t timestamp_ms;
    std::int16_t  temperature_raw;
    std::uint16_t crc16;
};

enum class BusError : std::uint8_t {
    Timeout,
    ArbitrationLost,
    NackReceived
};

// Контракт шини: чистий інтерфейс без прив'язки до вендорного HAL
class II2CBus {
public:
    virtual ~II2CBus() = default;
    virtual std::expected<void, BusError> write(std::span<const std::uint8_t> data) noexcept = 0;
    virtual void delay_ms(std::uint32_t ms) noexcept = 0;
};

// Сервіс обробки датчика: повністю ізольований для модульного тестування
class SensorService {
public:
    explicit SensorService(II2CBus& bus) noexcept : bus_(bus) {}

    PORT_RAM_FUNC
    std::expected<SensorDataPacket, BusError> read_packet() noexcept;

private:
    II2CBus& bus_;
};

} // namespace drivers::sensors

#endif // SENSOR_SERVICE_HPP
