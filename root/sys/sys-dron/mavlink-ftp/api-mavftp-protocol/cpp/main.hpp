#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <string_view>
#include <algorithm>

namespace mavftp {

constexpr size_t MaxDataLen = 239;
constexpr size_t HeaderSize = 12;
constexpr size_t TotalPayloadSize = HeaderSize + MaxDataLen; // 251

enum class Opcode : uint8_t {
    None             = 0,
    TerminateSession = 1,
    ResetSessions    = 2,
    ListDirectory    = 3,
    OpenFileRO       = 4,
    ReadFile         = 5,
    CreateFile       = 6,
    WriteFile        = 7,
    RemoveFile       = 8,
    CreateDirectory  = 9,
    RemoveDirectory  = 10,
    OpenFileWO       = 11,
    TruncateFile     = 12,
    Rename           = 13,
    CalcFileCRC32    = 14,
    BurstReadFile    = 15,
    Ack              = 128,
    Nak              = 129
};

enum class ErrorCode : uint8_t {
    None                = 0,
    Fail                = 1,
    FailErrno           = 2,
    InvalidDataSize     = 3,
    InvalidSession      = 4,
    NoSessionsAvailable = 5,
    EOF_Reached         = 6,
    UnknownCommand      = 7,
    FileExists          = 8,
    FileProtected       = 9,
    FileNotFound        = 10
};

#pragma pack(push, 1)
struct [[gnu::packed]] PayloadHeader {
    uint16_t seqNumber{0};
    uint8_t  session{0};
    Opcode   opcode{Opcode::None};
    uint8_t  size{0};
    Opcode   reqOpcode{Opcode::None};
    uint8_t  burstComplete{0};
    uint8_t  padding{0};
    uint32_t offset{0};
    uint8_t  data[MaxDataLen]{0};

    [[nodiscard]] std::span<const uint8_t> payloadData() const noexcept {
        return {data, std::min<size_t>(size, MaxDataLen)};
    }

    [[nodiscard]] std::span<uint8_t> mutableData() noexcept {
        return {data, MaxDataLen};
    }

    void setStringPayload(std::string_view str) noexcept {
        const size_t copyLen = std::min(str.size(), MaxDataLen - 1);
        std::memcpy(data, str.data(), copyLen);
        data[copyLen] = '\0';
        size = static_cast<uint8_t>(copyLen + 1);
    }
};
#pragma pack(pop)

static_assert(sizeof(PayloadHeader) == TotalPayloadSize, "PayloadHeader must be exactly 251 bytes");

} // namespace mavftp
