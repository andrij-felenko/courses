/* ============================================================================
 * ФАЙЛ: driver_core.hpp - C++20 Заголовок концептів та статичного драйвера
 * ============================================================================ */
#ifndef DRIVER_CORE_HPP
#define DRIVER_CORE_HPP

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <atomic>
#include <expected>
#include <concepts>
#include <optional>

namespace embed::driver {

enum class Status : uint8_t {
    Ok = 0,
    Busy,
    Timeout,
    Nack,
    BusError,
    Overflow,
    InvalidParam,
    Uninitialized
};

enum class OpType : uint8_t {
    Write = 0,
    Read,
    WriteRead
};

struct Transaction {
    uint8_t dev_addr{0};
    OpType op_type{OpType::Write};
    std::span<const uint8_t> tx_data{};
    std::span<uint8_t> rx_data{};
    uint32_t timeout_us{50'000};
};

struct DriverStats {
    uint32_t total_transfers{0};
    uint32_t successful_transfers{0};
    uint32_t nack_errors{0};
    uint32_t timeout_errors{0};
    uint32_t bus_recoveries{0};
};

/* Концепт апаратного периферійного блоку (Hardware Port) */
template <typename T>
concept HardwareBusRegister = requires(T hw, uint8_t byte) {
    { hw.write_data(byte) } -> std::same_as<void>;
    { hw.read_data() } -> std::same_as<uint8_t>;
    { hw.is_tx_empty() } -> std::same_as<bool>;
    { hw.is_rx_ready() } -> std::same_as<bool>;
    { hw.generate_start() } -> std::same_as<void>;
    { hw.generate_stop() } -> std::same_as<void>;
    { hw.is_nack() } -> std::same_as<bool>;
};

} // namespace embed::driver

#endif /* DRIVER_CORE_HPP */
