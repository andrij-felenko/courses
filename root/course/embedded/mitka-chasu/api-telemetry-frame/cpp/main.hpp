#include <cstdint>
#include <span>
#include <vector>
#include <optional>
#include <chrono>

enum class TimeMode : uint16_t {
    AbsoluteFull  = 0x0000,
    ForwardDelta  = 0x0001,
    ReverseAnchor = 0x0002,
    PeriodicFixed = 0x0003
};

enum class RtcStatus : uint16_t {
    Unsynchronized = 0x0000,
    Estimated      = 0x04,
    NtpSynced      = 0x08,
    GnssLocked     = 0x0C
};

enum class DeltaScale : uint16_t {
    Milliseconds = 0x0000,
    TenthsOfSec  = 0x0020,
    Seconds      = 0x0040
};

enum class CodecError {
    InvalidParameter,
    BufferOverflow,
    BadMagicByte,
    VersionMismatch,
    ChecksumFailure,
    UnsupportedMode
};

struct TelemetryPoint {
    std::chrono::milliseconds delta;
    int16_t raw_value;
};

struct DecodedMeasurement {
    std::chrono::system_clock::time_point timestamp;
    int16_t raw_value;
    RtcStatus clock_quality;
};

class TelemetryCodec {
public:
    static constexpr uint8_t Magic = 0x7E;
    static constexpr uint8_t Version = 0x01;

    // Пакування серії вимірів у бінарний буфер (Reverse Anchor)
    static std::optional<std::vector<uint8_t>> encode_reverse_delta(
        RtcStatus status,
        uint8_t sample_type,
        std::span<const TelemetryPoint> points
    );

    // Розпакування та відновлення часових міток на сервері
    static std::optional<std::vector<DecodedMeasurement>> decode_and_reconstruct(
        std::span<const uint8_t> packet,
        std::chrono::system_clock::time_point server_receive_time,
        std::chrono::milliseconds estimated_propagation_delay
    );
};
