#include <cstdint>
#include <array>
#include <span>
#include <expected>
#include <system_error>

enum class SdoClientCommand : uint8_t {
    WriteRequest = 1,
    ReadRequest  = 2
};

enum class SdoServerCommand : uint8_t {
    WriteResponse = 3,
    ReadResponse  = 2,
    Abort         = 4
};

enum class SdoAbortCode : uint32_t {
    ToggleBit            = 0x05030000,
    Timeout              = 0x05040001,
    UnsupportedAccess    = 0x06010000,
    ReadOnly             = 0x06010002,
    ObjectDoesNotExist   = 0x06020000,
    SubindexDoesNotExist = 0x06090011,
    ValueOutOfRange      = 0x06090030
};

struct SdoExpeditedRequest {
    uint16_t index;
    uint8_t subindex;
    uint32_t data;
    uint8_t data_len;
};

struct SdoResponse {
    uint16_t index;
    uint8_t subindex;
    uint32_t data;
    uint8_t data_len;
};

enum class SdoParseError {
    InvalidFrameLength,
    UnknownCommandSpecifier,
    InvalidDataLength,
    AbortReceived
};

class SdoCodec {
public:
    using FrameData = std::array<uint8_t, 8>;

    /* Упакування прискореного запису SDO Write Request із використанням C++20 std::expected */
    static std::expected<FrameData, SdoParseError> pack_expedited_write(const SdoExpeditedRequest& req) {
        if (req.data_len < 1 || req.data_len > 4) {
            return std::unexpected(SdoParseError::InvalidDataLength);
        }

        FrameData frame{};
        const uint8_t empty_bytes = static_cast<uint8_t>(4 - req.data_len);
        const uint8_t ccs = static_cast<uint8_t>(SdoClientCommand::WriteRequest);
        
        frame[0] = static_cast<uint8_t>((ccs << 5) | (empty_bytes << 2) | 0x02U | 0x01U);
        frame[1] = static_cast<uint8_t>(req.index & 0xFFU);
        frame[2] = static_cast<uint8_t>((req.index >> 8) & 0xFFU);
        frame[3] = req.subindex;

        frame[4] = static_cast<uint8_t>(req.data & 0xFFU);
        frame[5] = static_cast<uint8_t>((req.data >> 8) & 0xFFU);
        frame[6] = static_cast<uint8_t>((req.data >> 16) & 0xFFU);
        frame[7] = static_cast<uint8_t>((req.data >> 24) & 0xFFU);

        return frame;
    }

    /* Упакування прискореного запису SDO Read Request */
    static FrameData pack_read_request(uint16_t index, uint8_t subindex) {
        FrameData frame{};
        const uint8_t ccs = static_cast<uint8_t>(SdoClientCommand::ReadRequest);
        
        frame[0] = static_cast<uint8_t>(ccs << 5);
        frame[1] = static_cast<uint8_t>(index & 0xFFU);
        frame[2] = static_cast<uint8_t>((index >> 8) & 0xFFU);
        frame[3] = subindex;

        return frame;
    }

    /* Безпечний розбір кадру відповіді SDO з виділенням SdoAbortCode у разі помилки */
    static std::expected<SdoResponse, SdoAbortCode> parse_read_response(std::span<const uint8_t, 8> frame) {
        const uint8_t cmd = frame[0];
        const uint8_t scs = (cmd >> 5) & 0x07U;

        const uint16_t idx = static_cast<uint16_t>(frame[1]) | (static_cast<uint16_t>(frame[2]) << 8);
        const uint8_t sub_idx = frame[3];

        if (scs == static_cast<uint8_t>(SdoServerCommand::Abort)) {
            const uint32_t raw_abort = static_cast<uint32_t>(frame[4]) |
                                       (static_cast<uint32_t>(frame[5]) << 8) |
                                       (static_cast<uint32_t>(frame[6]) << 16) |
                                       (static_cast<uint32_t>(frame[7]) << 24);
            return std::unexpected(static_cast<SdoAbortCode>(raw_abort));
        }

        const uint8_t empty_bytes = (cmd >> 2) & 0x03U;
        const uint32_t payload = static_cast<uint32_t>(frame[4]) |
                                 (static_cast<uint32_t>(frame[5]) << 8) |
                                 (static_cast<uint32_t>(frame[6]) << 16) |
                                 (static_cast<uint32_t>(frame[7]) << 24);

        return SdoResponse{
            .index = idx,
            .subindex = sub_idx,
            .data = payload,
            .data_len = static_cast<uint8_t>(4 - empty_bytes)
        };
    }
};
