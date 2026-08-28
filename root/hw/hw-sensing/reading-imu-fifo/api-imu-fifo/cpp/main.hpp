#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>

namespace imu {

enum class FifoMode : uint8_t {
    Bypass     = 0x00,
    Stream     = 0x01,
    StopOnFull = 0x02
};

enum class Error : int32_t {
    BusFailure    = -1,
    FifoOverflow  = -2,
    FrameSyncLoss = -3,
    Timeout       = -4,
    InvalidParam  = -5,
    NullPointer   = -6
};

struct Sample {
    std::array<float, 3> accel_mps2{};
    std::array<float, 3> gyro_radps{};
    float                temp_celsius{0.0f};
    uint32_t             timestamp_us{0};
    bool                 has_accel{false};
    bool                 has_gyro{false};
    bool                 fsync_event{false};
};

struct FifoConfig {
    FifoMode mode{FifoMode::Stream};
    uint16_t watermark_bytes{160};
    bool     enable_accel{true};
    bool     enable_gyro{true};
    bool     enable_timestamp{true};
    bool     enable_hires_20bit{false};
};

class IFifoTransport {
public:
    virtual ~IFifoTransport() = default;
    virtual std::expected<void, Error> read_registers(uint8_t reg, std::span<uint8_t> dst) = 0;
    virtual std::expected<void, Error> write_register(uint8_t reg, uint8_t val) = 0;
    virtual std::expected<void, Error> start_dma_burst_read(uint8_t fifo_reg, std::span<uint8_t> dst) = 0;
};

class FifoController {
public:
    explicit FifoController(IFifoTransport &transport) : transport_{transport} {}

    std::expected<void, Error> configure(const FifoConfig &cfg);
    std::expected<void, Error> flush();
    std::expected<uint16_t, Error> available_bytes();
    
    std::expected<size_t, Error> parse_packet_stream(
        std::span<const uint8_t> raw_bytes,
        std::span<Sample> out_samples
    );

private:
    IFifoTransport &transport_;
    FifoConfig      active_config_{};
};

} // namespace imu
