#include <span>
#include <cstdint>
#include <expected>
#include <array>

namespace gateway_protocol {

enum class Opcode : uint8_t {
    Discovery          = 0x01,
    DiscoveryResp     = 0x81,
    AuthChallenge     = 0x02,
    AuthResp          = 0x82,
    ManifestNegotiate = 0x03,
    ManifestAck       = 0x83,
    PushChunk         = 0x04,
    ChunkAck          = 0x84,
    CommitAndTest     = 0x05,
    CommitResp        = 0x85
};

struct [[gnu::packed]] FrameHeader {
    uint8_t seq_id;
    Opcode opcode;
    uint16_t payload_len;
};

struct [[gnu::packed]] ManifestPayload {
    uint32_t target_version;
    uint32_t total_payload_size;
    uint16_t chunk_size;
    std::array<uint8_t, 32> full_sha256;
    std::array<uint8_t, 64> signature_ed25519;
};

struct [[gnu::packed]] ChunkPayload {
    uint16_t chunk_index;
    uint16_t chunk_crc16;
    std::array<uint8_t, 256> data;
};

class GatewaySession {
public:
    enum class ParseError {
        CrcMismatch,
        PayloadLengthMismatch,
        UnknownOpcode
    };

    std::expected<void, ParseError>
    processFrame(const FrameHeader& hdr,
                 std::span<const uint8_t> payload,
                 uint32_t packet_crc,
                 uint32_t expected_crc) {
        if (packet_crc != expected_crc) {
            return std::unexpected(ParseError::CrcMismatch);
        }
        if (payload.size() != hdr.payload_len) {
            return std::unexpected(ParseError::PayloadLengthMismatch);
        }

        switch (hdr.opcode) {
            case Opcode::ManifestNegotiate:
                return handleManifest(payload);
            case Opcode::PushChunk:
                return handleChunk(payload);
            default:
                return std::unexpected(ParseError::UnknownOpcode);
        }
    }

private:
    std::expected<void, ParseError> handleManifest(std::span<const uint8_t> bytes) {
        if (bytes.size() < sizeof(ManifestPayload)) {
            return std::unexpected(ParseError::PayloadLengthMismatch);
        }
        const auto* manifest = reinterpret_cast<const ManifestPayload*>(bytes.data());
        (void)manifest;
        return {};
    }

    std::expected<void, ParseError> handleChunk(std::span<const uint8_t> bytes) {
        if (bytes.size() < sizeof(ChunkPayload)) {
            return std::unexpected(ParseError::PayloadLengthMismatch);
        }
        const auto* chunk = reinterpret_cast<const ChunkPayload*>(bytes.data());
        (void)chunk;
        return {};
    }
};

} // namespace gateway_protocol
