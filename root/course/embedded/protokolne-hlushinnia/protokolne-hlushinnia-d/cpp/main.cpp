#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

namespace embedded::security {

enum class FrameType : uint8_t {
    Data        = 0x01,
    Heartbeat   = 0x02,
    Disconnect  = 0x03,
    Ack         = 0x04
};

enum class LinkMode : uint8_t {
    CooperativeCsma = 0,
    ForcedTx        = 1,
    ChannelHop      = 2
};

enum class LinkError {
    PayloadTooLarge,
    BufferTooSmall,
    AuthenticationFailed,
    ReplayDetected,
    WrongDestination,
    MalformedHeader
};

#pragma pack(push, 1)
struct FrameHeader {
    FrameType type;
    uint8_t   src_id;
    uint8_t   dst_id;
    LinkMode  flags;
    uint32_t  seq_num;
};
#pragma pack(pop)

class SecureLinkDriver {
public:
    static constexpr size_t MaxPayloadSize   = 64;
    static constexpr size_t AuthTagSize      = 8;
    static constexpr size_t HeaderSize       = sizeof(FrameHeader);
    static constexpr size_t MaxPacketSize    = HeaderSize + MaxPayloadSize + AuthTagSize;
    static constexpr size_t ReplayWindowSize = 32;
    static constexpr uint8_t MaxFailures     = 5;

    constexpr SecureLinkDriver(uint8_t node_id, std::span<const uint8_t, 16> key) noexcept
        : node_id_{node_id} {
        std::copy(key.begin(), key.end(), shared_key_.begin());
    }

    [[nodiscard]] std::expected<size_t, LinkError> build_packet(
        uint8_t dst_id,
        FrameType type,
        std::span<const uint8_t> payload,
        std::span<uint8_t> out_buffer) noexcept {
        
        if (payload.size() > MaxPayloadSize) {
            return std::unexpected(LinkError::PayloadTooLarge);
        }
        
        const size_t total_size = HeaderSize + payload.size() + AuthTagSize;
        if (out_buffer.size() < total_size) {
            return std::unexpected(LinkError::BufferTooSmall);
        }

        FrameHeader header{
            .type = type,
            .src_id = node_id_,
            .dst_id = dst_id,
            .flags = current_mode_,
            .seq_num = ++tx_seq_
        };

        std::copy_n(reinterpret_cast<const uint8_t*>(&header), HeaderSize, out_buffer.begin());
        if (!payload.empty()) {
            std::copy(payload.begin(), payload.end(), out_buffer.begin() + HeaderSize);
        }

        const auto tag = calculate_mac(out_buffer.subspan(0, HeaderSize + payload.size()));
        std::copy(tag.begin(), tag.end(), out_buffer.begin() + HeaderSize + payload.size());

        return total_size;
    }

    [[nodiscard]] std::expected<std::span<const uint8_t>, LinkError> process_rx(
        std::span<const uint8_t> raw_packet) noexcept {
        
        if (raw_packet.size() < HeaderSize + AuthTagSize) {
            register_anomaly();
            return std::unexpected(LinkError::MalformedHeader);
        }

        const size_t payload_len = raw_packet.size() - HeaderSize - AuthTagSize;
        const auto received_tag = raw_packet.last<AuthTagSize>();
        const auto expected_tag = calculate_mac(raw_packet.first(HeaderSize + payload_len));

        // 1. Криптографічна автентифікація
        if (!std::equal(received_tag.begin(), received_tag.end(), expected_tag.begin())) {
            register_anomaly();
            return std::unexpected(LinkError::AuthenticationFailed);
        }

        FrameHeader header;
        std::copy_n(raw_packet.data(), HeaderSize, reinterpret_cast<uint8_t*>(&header));

        // 2. Перевірка адреси
        if (header.dst_id != node_id_ && header.dst_id != 0xFF) {
            return std::unexpected(LinkError::WrongDestination);
        }

        // 3. Захист від Replay
        if (!verify_replay(header.seq_num)) {
            register_anomaly();
            return std::unexpected(LinkError::ReplayDetected);
        }

        if (header.type == FrameType::Disconnect) {
            is_connected_ = false;
            return std::span<const uint8_t>{};
        }

        if (anomaly_score_ > 0) {
            --anomaly_score_;
        }

        return raw_packet.subspan(HeaderSize, payload_len);
    }

    template <typename CcaCheckFn, typename SendFn>
    void transmit(std::span<const uint8_t> packet, CcaCheckFn&& cca_is_free, SendFn&& send_raw) noexcept {
        if (current_mode_ == LinkMode::CooperativeCsma) {
            size_t wait_ticks = 0;
            while (!cca_is_free()) {
                if (++wait_ticks > 100) {
                    // Перехід в аварійний режим Forced TX при виявленні блокування
                    current_mode_ = LinkMode::ForcedTx;
                    break;
                }
            }
        }

        send_raw(packet);
    }

    [[nodiscard]] LinkMode mode() const noexcept { return current_mode_; }
    [[nodiscard]] bool is_connected() const noexcept { return is_connected_; }

private:
    [[nodiscard]] std::array<uint8_t, AuthTagSize> calculate_mac(std::span<const uint8_t> data) const noexcept {
        uint32_t hash = 0x811c9dc5;
        for (uint8_t k : shared_key_) {
            hash = (hash ^ k) * 0x01000193;
        }
        for (uint8_t byte : data) {
            hash = (hash ^ byte) * 0x01000193;
        }

        std::array<uint8_t, AuthTagSize> tag{};
        std::copy_n(reinterpret_cast<const uint8_t*>(&hash), 4, tag.begin());
        hash = ~hash;
        std::copy_n(reinterpret_cast<const uint8_t*>(&hash), 4, tag.begin() + 4);
        return tag;
    }

    bool verify_replay(uint32_t seq) noexcept {
        if (seq > rx_last_seq_) {
            const uint32_t diff = seq - rx_last_seq_;
            if (diff < ReplayWindowSize) {
                replay_mask_ <<= diff;
                replay_mask_ |= 1;
            } else {
                replay_mask_ = 1;
            }
            rx_last_seq_ = seq;
            return true;
        }

        const uint32_t diff = rx_last_seq_ - seq;
        if (diff >= ReplayWindowSize || (replay_mask_ & (1UL << diff))) {
            return false;
        }

        replay_mask_ |= (1UL << diff);
        return true;
    }

    void register_anomaly() noexcept {
        if (++anomaly_score_ >= MaxFailures) {
            current_mode_ = LinkMode::ForcedTx;
        }
    }

    uint8_t node_id_;
    std::array<uint8_t, 16> shared_key_{};
    uint32_t tx_seq_{0};
    uint32_t rx_last_seq_{0};
    uint32_t replay_mask_{0};
    uint8_t  anomaly_score_{0};
    LinkMode current_mode_{LinkMode::CooperativeCsma};
    bool     is_connected_{true};
};

} // namespace embedded::security
