#include <cstdint>
#include <cstring>
#include <span>
#include <string_view>
#include <algorithm>

namespace mavftp {

constexpr size_t MaxDataSize = 239;
constexpr size_t TotalPayloadSize = 12 + MaxDataSize; // 251 байт

enum class Command : uint8_t {
    None             = 0,
    TerminateSession = 1,
    ResetSessions    = 2,
    ListDirectory    = 3,
    OpenFileRO       = 4,
    ReadFile         = 5,
    CreateFile       = 6,
    WriteFile        = 7,
    RemoveFile       = 8,
    BurstReadFile    = 15,
    Ack              = 128,
    Nak              = 129
};

#pragma pack(push, 1)
struct [[gnu::packed]] PayloadHeader {
    uint16_t seqNumber{0};
    uint8_t  session{0};
    Command  opcode{Command::None};
    uint8_t  size{0};
    Command  reqOpcode{Command::None};
    uint8_t  burstComplete{0};
    uint8_t  padding{0};
    uint32_t offset{0};
    uint8_t  data[MaxDataSize]{0};

    [[nodiscard]] std::span<const uint8_t> payloadData() const noexcept {
        return {data, std::min<size_t>(size, MaxDataSize)};
    }

    void setPath(std::string_view path) noexcept {
        const size_t copyLen = std::min(path.size(), MaxDataSize - 1);
        std::memcpy(data, path.data(), copyLen);
        data[copyLen] = '\0';
        size = static_cast<uint8_t>(copyLen + 1);
    }
};
#pragma pack(pop)

static_assert(sizeof(PayloadHeader) == TotalPayloadSize, "PayloadHeader size must be 251 bytes");

} // namespace mavftp
