#include <cstdint>
#include <array>
#include <span>

#pragma pack(push, 1)

struct PtpClockIdentity {
    std::array<uint8_t, 8> id;
};

struct PtpPortIdentity {
    PtpClockIdentity clock_id;
    uint16_t         port_number;
};

struct PtpTimestamp {
    uint16_t seconds_high;
    uint32_t seconds_low;
    uint32_t nanoseconds;

    [[nodiscard]] uint64_t total_seconds() const noexcept {
        return (static_cast<uint64_t>(seconds_high) << 32) | seconds_low;
    }
};

struct PtpHeader {
    uint8_t  transport_and_type;
    uint8_t  version_ptp;
    uint16_t message_length;
    uint8_t  domain_number;
    uint8_t  minor_version;
    std::array<uint8_t, 2> flags;
    int64_t  correction_field;
    uint32_t reserved;
    PtpPortIdentity source_port_id;
    uint16_t sequence_id;
    uint8_t  control_field;
    int8_t   log_message_interval;

    [[nodiscard]] uint8_t message_type() const noexcept {
        return transport_and_type & 0x0F;
    }

    [[nodiscard]] bool is_two_step() const noexcept {
        return (flags[0] & 0x02) != 0;
    }

    [[nodiscard]] double correction_nanoseconds() const noexcept {
        return static_cast<double>(correction_field) / 65536.0;
    }
};

struct PtpFollowUpMsg {
    PtpHeader    header;
    PtpTimestamp precise_origin_timestamp;
};

struct PtpDelayRespMsg {
    PtpHeader       header;
    PtpTimestamp    receive_timestamp;
    PtpPortIdentity requesting_port_id;
};

#pragma pack(pop)
