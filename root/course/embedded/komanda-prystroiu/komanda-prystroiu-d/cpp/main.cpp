#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <expected>
#include <algorithm>

namespace iot::control {

inline constexpr uint32_t CmdMagic = 0x434D4431; // "CMD1"
inline constexpr size_t RingBufferSize = 16;
inline constexpr size_t MaxPayloadSize = 32;

enum class CommandType : uint16_t {
    Noop         = 0x00,
    SetRelay     = 0x01,
    MoveStepper  = 0x02,
    Calibrate    = 0x03
};

enum class CommandState : uint8_t {
    Free       = 0x00,
    Accepted   = 0x01,
    Executing  = 0x02,
    Succeeded  = 0x03,
    Failed     = 0x04,
    Expired    = 0x05
};

enum class CommandError : int32_t {
    Ok             = 0,
    InvalidMagic   = -1,
    CrcMismatch    = -2,
    Expired        = -3,
    Busy           = -4,
    HardwareFault  = -5,
    BufferTooSmall = -6
};

#pragma pack(push, 1)
struct CommandPacket {
    uint32_t magic;
    uint64_t token;
    CommandType cmd_type;
    uint32_t ttl_ms;
    uint16_t payload_len;
    std::array<uint8_t, MaxPayloadSize> payload;
    uint32_t crc32;
};
#pragma pack(pop)

struct IdempotencyRecord {
    uint64_t token{0};
    CommandType type{CommandType::Noop};
    CommandState state{CommandState::Free};
    CommandError result_code{CommandError::Ok};
    uint32_t rx_time_ms{0};
    uint32_t ttl_ms{0};
};

class CommandDispatcher {
public:
    explicit CommandDispatcher() = default;

    // Інтерфейс зворотного зв'язку для відправки квитанцій
    class IAckTransport {
    public:
        virtual ~IAckTransport() = default;
        virtual void send_phase1_ack(uint64_t token, CommandState state) = 0;
        virtual void send_phase2_ack(uint64_t token, CommandState state, CommandError result) = 0;
        virtual uint32_t uptime_ms() const = 0;
    };

    std::expected<void, CommandError> process_packet(std::span<const uint8_t> raw_bytes, IAckTransport& transport) {
        if (raw_bytes.size() < sizeof(CommandPacket)) {
            return std::unexpected(CommandError::BufferTooSmall);
        }

        const auto* packet = reinterpret_cast<const CommandPacket*>(raw_bytes.data());

        // 1. Валідація магічного заголовка та CRC32
        if (packet->magic != CmdMagic) {
            return std::unexpected(CommandError::InvalidMagic);
        }

        if (calculate_crc32(raw_bytes.subspan(0, sizeof(CommandPacket) - sizeof(uint32_t))) != packet->crc32) {
            return std::unexpected(CommandError::CrcMismatch);
        }

        const uint32_t now = transport.uptime_ms();

        // 2. Ідемпотентна дедуплікація
        if (auto* existing = find_slot(packet->token); existing != nullptr) {
            if (existing->state == CommandState::Succeeded || existing->state == CommandState::Failed) {
                transport.send_phase2_ack(existing->token, existing->state, existing->result_code);
                return {};
            }
            if (existing->state == CommandState::Executing) {
                transport.send_phase1_ack(existing->token, CommandState::Executing);
                return {};
            }
        }

        // 3. Перевірка TTL
        if (packet->ttl_ms > 0 && packet->ttl_ms < 50) {
            transport.send_phase2_ack(packet->token, CommandState::Expired, CommandError::Expired);
            return std::unexpected(CommandError::Expired);
        }

        // 4. Фіксація в кільцевому буфері та Фаза 1 ACK
        auto& slot = allocate_slot(packet->token, packet->cmd_type, now, packet->ttl_ms);
        transport.send_phase1_ack(packet->token, CommandState::Accepted);

        // 5. Виконання апаратної дії
        slot.state = CommandState::Executing;
        active_token_ = packet->token;
        exec_start_ms_ = now;
        exec_timeout_ms_ = (packet->ttl_ms > 0) ? packet->ttl_ms : 5000;

        auto exec_res = execute_hardware(slot.type, std::span{packet->payload.data(), packet->payload_len});
        if (!exec_res.has_value()) {
            slot.state = CommandState::Failed;
            slot.result_code = exec_res.error();
            transport.send_phase2_ack(slot.token, CommandState::Failed, exec_res.error());
            return std::unexpected(exec_res.error());
        }

        if (slot.type == CommandType::SetRelay || slot.type == CommandType::Noop) {
            slot.state = CommandState::Succeeded;
            slot.result_code = CommandError::Ok;
            transport.send_phase2_ack(slot.token, CommandState::Succeeded, CommandError::Ok);
            active_token_ = 0;
        }

        return {};
    }

    void tick(IAckTransport& transport) {
        if (active_token_ == 0) return;

        auto* slot = find_slot(active_token_);
        if (!slot || slot->state != CommandState::Executing) {
            active_token_ = 0;
            return;
        }

        const uint32_t now = transport.uptime_ms();
        if (now - exec_start_ms_ > exec_timeout_ms_) {
            slot->state = CommandState::Expired;
            slot->result_code = CommandError::Expired;
            transport.send_phase2_ack(slot->token, CommandState::Expired, CommandError::Expired);
            active_token_ = 0;
        }
    }

private:
    std::array<IdempotencyRecord, RingBufferSize> ring_{};
    size_t ring_head_{0};
    uint64_t active_token_{0};
    uint32_t exec_start_ms_{0};
    uint32_t exec_timeout_ms_{0};

    [[nodiscard]] IdempotencyRecord* find_slot(uint64_t token) noexcept {
        auto it = std::find_if(ring_.begin(), ring_.end(), [token](const IdempotencyRecord& rec) {
            return rec.state != CommandState::Free && rec.token == token;
        });
        return (it != ring_.end()) ? &(*it) : nullptr;
    }

    IdempotencyRecord& allocate_slot(uint64_t token, CommandType type, uint32_t now_ms, uint32_t ttl_ms) noexcept {
        auto& slot = ring_[ring_head_];
        ring_head_ = (ring_head_ + 1) % RingBufferSize;

        slot.token       = token;
        slot.type        = type;
        slot.state       = CommandState::Accepted;
        slot.result_code = CommandError::Ok;
        slot.rx_time_ms  = now_ms;
        slot.ttl_ms      = ttl_ms;
        return slot;
    }

    static std::expected<void, CommandError> execute_hardware(CommandType type, std::span<const uint8_t> payload) noexcept {
        switch (type) {
            case CommandType::SetRelay:
                if (payload.empty()) return std::unexpected(CommandError::HardwareFault);
                // Прямий запис у виводи GPIO
                return {};
            case CommandType::MoveStepper:
            case CommandType::Calibrate:
                return {};
            default:
                return {};
        }
    }

    static uint32_t calculate_crc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320 & (-(int32_t)(crc & 1)));
            }
        }
        return ~crc;
    }
};

} // namespace iot::control
