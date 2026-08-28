// hal_i2c_interface.hpp — Інтерфейс шини I2C у сучасному C++
#pragma once
#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace hal {

enum class BusStatus {
    Ok,
    ErrorNack,
    ErrorTimeout
};

class II2cMaster {
public:
    virtual ~II2cMaster() = default;
    virtual std::expected<void, BusStatus> write(uint8_t dev_addr, 
                                                 std::span<const uint8_t> data) = 0;
    virtual std::expected<void, BusStatus> read(uint8_t dev_addr, 
                                                std::span<uint8_t> data) = 0;
    virtual std::expected<void, BusStatus> write_read(uint8_t dev_addr, 
                                                      std::span<const uint8_t> wdata, 
                                                      std::span<uint8_t> rdata) = 0;
};

} // namespace hal
