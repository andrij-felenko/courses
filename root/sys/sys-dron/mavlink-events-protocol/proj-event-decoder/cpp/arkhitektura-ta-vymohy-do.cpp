#include <cstdint>
#include <array>
#include <span>
#include <optional>
#include <cstring>
#include <algorithm>

struct StoredEvent {
    uint32_t                id{0};
    uint32_t                timeBootMs{0};
    uint16_t                sequence{0};
    uint8_t                 destinationComponent{0};
    uint8_t                 destinationSystem{0};
    uint8_t                 logLevels{0};
    std::array<uint8_t, 40> arguments{};
    uint8_t                 payloadLength{0};
};

template <size_t BufferSize = 32>
class AutopilotEventBuffer {
public:
    uint16_t push(uint32_t id,
                  uint32_t timeBootMs,
                  uint8_t logLevels,
                  std::span<const uint8_t> args) noexcept {
        const uint16_t seq = m_headSequence;
        const size_t idx = seq % BufferSize;

        auto& ev = m_buffer[idx];
        ev.id = id;
        ev.timeBootMs = timeBootMs;
        ev.sequence = seq;
        ev.destinationComponent = 0;
        ev.destinationSystem = 0;
        ev.logLevels = logLevels;

        const size_t copyBytes = std::min(args.size(), ev.arguments.size());
        std::memcpy(ev.arguments.data(), args.data(), copyBytes);
        if (copyBytes < ev.arguments.size()) {
            std::memset(ev.arguments.data() + copyBytes, 0, ev.arguments.size() - copyBytes);
        }
        ev.payloadLength = static_cast<uint8_t>(13 + copyBytes);

        m_headSequence = static_cast<uint16_t>((seq + 1) & 0xFFFF);
        if (m_hasWrapped) {
            m_oldestSequence = static_cast<uint16_t>((m_oldestSequence + 1) & 0xFFFF);
        } else if (m_headSequence >= BufferSize) {
            m_hasWrapped = true;
            m_oldestSequence = 0;
        }

        return seq;
    }

    [[nodiscard]] std::optional<StoredEvent> get(uint16_t sequence) const noexcept {
        const uint16_t diff = static_cast<uint16_t>(m_headSequence - sequence);
        if (diff == 0 || diff > BufferSize) {
            return std::nullopt;
        }

        const size_t idx = sequence % BufferSize;
        if (m_buffer[idx].sequence == sequence) {
            return m_buffer[idx];
        }
        return std::nullopt;
    }

    [[nodiscard]] uint16_t headSequence() const noexcept { return m_headSequence; }

private:
    std::array<StoredEvent, BufferSize> m_buffer{};
    uint16_t m_headSequence{0};
    uint16_t m_oldestSequence{0};
    bool     m_hasWrapped{false};
};
