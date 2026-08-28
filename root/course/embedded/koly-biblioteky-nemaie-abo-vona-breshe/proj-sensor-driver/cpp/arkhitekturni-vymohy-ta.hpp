#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <expected>

namespace driver {

enum class Status : int8_t {
    Ok = 0,
    NullPointer = -1,
    BusIo = -2,
    BusTimeout = -3,
    ChipIdMismatch = -4,
    CrcMismatch = -5,
    NotReady = -6,
    InvalidState = -7,
    DataOutOfRange = -8,
    BusStuck = -9
};

enum class State : uint8_t {
    Uninitialized = 0,
    Idle,
    Converting,
    DataReady,
    Error
};

struct SensorData {
    int32_t  temperature_mdeg_c{0}; // 25150 = 25.15 °C
    uint32_t humidity_mpercent{0};  // 48500 = 48.50 %
    uint32_t pressure_pa{0};        // 101325 Pa
    uint32_t timestamp_us{0};
};

/* C++20 Концепт апаратного транспорту шини */
template <typename T>
concept BusTransport = requires(T bus, uint8_t reg, std::span<uint8_t> rx, std::span<const uint8_t> tx) {
    { bus.read(reg, rx) } -> std::same_as<Status>;
    { bus.write(reg, tx) } -> std::same_as<Status>;
    { bus.get_time_us() } -> std::same_as<uint32_t>;
    { bus.recover() } -> std::same_as<Status>;
};

template <BusTransport Transport>
class SensorDevice {
public:
    explicit SensorDevice(Transport& bus) noexcept
        : m_bus(bus), m_state(State::Uninitialized), m_conv_start_us(0) {}

    [[nodiscard]] Status init() noexcept;
    [[nodiscard]] Status start_measurement() noexcept;
    [[nodiscard]] std::expected<SensorData, Status> poll() noexcept;
    void reset_fsm() noexcept;
    [[nodiscard]] Status recover_bus() noexcept;

    [[nodiscard]] State state() const noexcept { return m_state; }
    [[nodiscard]] static uint8_t compute_crc8(std::span<const uint8_t> data) noexcept;

private:
    Transport& m_bus;
    State      m_state{State::Uninitialized};
    uint32_t   m_conv_start_us{0};
    static constexpr uint32_t CONV_DURATION_US = 20000; // 20 мс
    static constexpr uint8_t  REG_CHIP_ID = 0xD0;
    static constexpr uint8_t  EXPECTED_CHIP_ID = 0x58;
    static constexpr uint8_t  REG_MEAS_START = 0xF4;
    static constexpr uint8_t  REG_DATA_BURST = 0xF7;
    uint8_t    m_raw_buf[7]{0};
};

} // namespace driver
