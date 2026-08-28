#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <functional>
#include <expected>

enum class NetPriority : uint8_t {
    Low = 0,
    Normal = 1,
    Critical = 2
};

enum class NetState : uint8_t {
    Offline,
    Connecting,
    Online,
    Sleeping,
    Error
};

enum class NetError : uint8_t {
    BufferFull,
    LinkDown,
    InvalidPayload,
    Timeout
};

struct NetPacket {
    uint16_t msg_id{0};
    std::array<uint8_t, 64> payload{};
    uint8_t len{0};
    NetPriority priority{NetPriority::Normal};

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return std::span<const uint8_t>(payload.data(), len);
    }
};

class INetAdapter {
public:
    using RxCallback = std::function<void(const NetPacket&)>;

    virtual ~INetAdapter() = default;
    [[nodiscard]] virtual bool init() noexcept = 0;
    virtual void poll(uint32_t now_ms) noexcept = 0;
    [[nodiscard]] virtual std::expected<void, NetError> send(const NetPacket& pkt) noexcept = 0;
    [[nodiscard]] virtual NetState state() const noexcept = 0;
    virtual void set_rx_callback(RxCallback cb) noexcept = 0;
};
