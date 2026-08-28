#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>
#include <functional>

namespace embedded::camera {

inline constexpr size_t ChunkPayloadMax = 1400;
inline constexpr size_t DmaBufferSize   = 2048;
inline constexpr uint32_t ProtoMagic    = 0x56494445U; // "VIDE"

enum class PacketFlag : uint16_t {
    None       = 0,
    FirstChunk = 1U << 0,
    LastChunk  = 1U << 1
};

[[nodiscard]] constexpr PacketFlag operator|(PacketFlag a, PacketFlag b) noexcept {
    return static_cast<PacketFlag>(static_cast<uint16_t>(a) | static_cast<uint16_t>(b));
}

#pragma pack(push, 1)
struct FramePacketHeader {
    uint32_t magic{ProtoMagic};
    uint16_t frameId{0};
    uint16_t chunkIdx{0};
    uint16_t payloadLen{0};
    PacketFlag flags{PacketFlag::None};
    uint32_t crc32{0};
};
#pragma pack(pop)

struct FramePacket {
    FramePacketHeader header{};
    std::array<uint8_t, ChunkPayloadMax> payload{};

    [[nodiscard]] std::span<const uint8_t> payloadSpan() const noexcept {
        return {payload.data(), header.payloadLen};
    }
};

enum class FsmState : uint8_t {
    SearchSoi,
    StreamPayload,
    FrameComplete
};

struct StreamStatistics {
    uint32_t framesCaptured{0};
    uint32_t framesDropped{0};
    uint32_t bytesProcessed{0};
    uint32_t chunksTransmitted{0};
};

class DvpStreamParser {
public:
    using PacketTransmitter = std::function<bool(std::span<const uint8_t>)>;

    explicit DvpStreamParser(PacketTransmitter txCallback) noexcept
        : transmitter_(std::move(txCallback)) {}

    void processDmaChunk(std::span<const uint8_t> dmaBuffer) noexcept {
        for (uint8_t byte : dmaBuffer) {
            stats_.bytesProcessed++;

            switch (state_) {
                case FsmState::SearchSoi:
                    handleSearchSoi(byte);
                    break;

                case FsmState::StreamPayload:
                    handleStreamPayload(byte);
                    break;

                case FsmState::FrameComplete:
                    state_ = FsmState::SearchSoi;
                    prevByteWasFf_ = false;
                    break;
            }
        }
    }

    [[nodiscard]] const StreamStatistics& statistics() const noexcept {
        return stats_;
    }

    void reset() noexcept {
        state_ = FsmState::SearchSoi;
        currentChunkIdx_ = 0;
        prevByteWasFf_ = false;
        currentPacket_.header.payloadLen = 0;
    }

private:
    static constexpr uint8_t MarkerPrefix = 0xFFU;
    static constexpr uint8_t MarkerSoi    = 0xD8U;
    static constexpr uint8_t MarkerEoi    = 0xD9U;

    static uint32_t computeCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (uint8_t byte : data) {
            crc ^= static_cast<uint32_t>(byte);
            for (uint8_t bit = 0; bit < 8; ++bit) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
            }
        }
        return ~crc;
    }

    void flushCurrentChunk(bool isLast) noexcept {
        if (currentPacket_.header.payloadLen == 0 && !isLast) {
            return;
        }

        currentPacket_.header.magic = ProtoMagic;
        currentPacket_.header.frameId = currentFrameId_;
        currentPacket_.header.chunkIdx = currentChunkIdx_;
        
        auto flags = PacketFlag::None;
        if (currentChunkIdx_ == 0) flags = flags | PacketFlag::FirstChunk;
        if (isLast) flags = flags | PacketFlag::LastChunk;
        currentPacket_.header.flags = flags;

        currentPacket_.header.crc32 = computeCrc32(currentPacket_.payloadSpan());

        const size_t totalBytes = sizeof(FramePacketHeader) + currentPacket_.header.payloadLen;
        const auto* rawPtr = reinterpret_cast<const uint8_t*>(&currentPacket_);
        
        if (transmitter_) {
            transmitter_(std::span<const uint8_t>(rawPtr, totalBytes));
        }

        stats_.chunksTransmitted++;
        currentChunkIdx_++;
        currentPacket_.header.payloadLen = 0;
    }

    void handleSearchSoi(uint8_t byte) noexcept {
        if (prevByteWasFf_ && byte == MarkerSoi) {
            state_ = FsmState::StreamPayload;
            currentChunkIdx_ = 0;
            currentPacket_.payload[0] = MarkerPrefix;
            currentPacket_.payload[1] = MarkerSoi;
            currentPacket_.header.payloadLen = 2;
            prevByteWasFf_ = false;
        } else {
            prevByteWasFf_ = (byte == MarkerPrefix);
        }
    }

    void handleStreamPayload(uint8_t byte) noexcept {
        if (prevByteWasFf_ && byte == MarkerEoi) {
            if (currentPacket_.header.payloadLen < ChunkPayloadMax) {
                currentPacket_.payload[currentPacket_.header.payloadLen++] = byte;
            }
            flushCurrentChunk(true);
            
            stats_.framesCaptured++;
            currentFrameId_++;
            state_ = FsmState::SearchSoi;
            prevByteWasFf_ = false;
            return;
        }

        currentPacket_.payload[currentPacket_.header.payloadLen++] = byte;
        prevByteWasFf_ = (byte == MarkerPrefix);

        if (currentPacket_.header.payloadLen >= ChunkPayloadMax) {
            flushCurrentChunk(false);
        }
    }

    FsmState state_{FsmState::SearchSoi};
    uint16_t currentFrameId_{1};
    uint16_t currentChunkIdx_{0};
    bool prevByteWasFf_{false};
    FramePacket currentPacket_{};
    StreamStatistics stats_{};
    PacketTransmitter transmitter_;
};

} // namespace embedded::camera
