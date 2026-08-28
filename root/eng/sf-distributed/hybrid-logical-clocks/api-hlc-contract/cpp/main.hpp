#pragma once

#include <cstdint>
#include <chrono>
#include <compare>
#include <expected>
#include <memory>
#include <span>

namespace hlc {

enum class Status : uint8_t {
    Ok = 0,
    ClockDriftExceeded = 1,
    CounterOverflow = 2,
    InvalidArgument = 3
};

/* Канонічна незмінна мітка HLC */
struct Timestamp {
    uint64_t physical_ms{0};
    uint32_t logical{0};
    uint32_t node_id{0};

    auto operator<=>(const Timestamp&) const = default;

    [[nodiscard]] uint64_t to_wire64() const noexcept {
        return ((physical_ms & 0x0000FFFFFFFFFFFFULL) << 16) | (logical & 0xFFFFULL);
    }

    [[nodiscard]] static Timestamp from_wire64(uint64_t wire, uint32_t node_id = 0) noexcept {
        return Timestamp{
            .physical_ms = (wire >> 16) & 0x0000FFFFFFFFFFFFULL,
            .logical = static_cast<uint32_t>(wire & 0xFFFFULL),
            .node_id = node_id
        };
    }
};

/* Абстрактний інтерфейс годинникового рушія */
class IEngine {
public:
    virtual ~IEngine() = default;

    [[nodiscard]] virtual std::expected<Timestamp, Status> now() noexcept = 0;
    [[nodiscard]] virtual std::expected<Timestamp, Status> update(const Timestamp& remote_ts) noexcept = 0;
    [[nodiscard]] virtual uint32_t node_id() const noexcept = 0;
    [[nodiscard]] virtual std::chrono::milliseconds max_drift() const noexcept = 0;
};

/* Фабрика створення стандартного потокобезпечного рушія */
std::unique_ptr<IEngine> create_engine(uint32_t node_id,
                                       std::chrono::milliseconds max_drift = std::chrono::milliseconds(500));

} // namespace hlc
