#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <expected>
#include <optional>
#include <type_traits>

namespace embedded::config {

inline constexpr std::uint32_t ConfigMagic = 0x43464731U;

enum class Type : std::uint8_t {
    Bool   = 0x01,
    Int32  = 0x02,
    Uint32 = 0x03,
    Float  = 0x04,
    String = 0x05,
    Blob   = 0x06
};

enum class Flags : std::uint16_t {
    None         = 0x0000,
    ReadOnly     = 0x0001,
    RebootReq    = 0x0002,
    Confidential = 0x0004,
    Volatile     = 0x0008,
    TrialCrit    = 0x0010
};

constexpr Flags operator|(Flags a, Flags b) noexcept {
    return static_cast<Flags>(static_cast<std::uint16_t>(a) | static_cast<std::uint16_t>(b));
}

constexpr bool operator&(Flags a, Flags b) noexcept {
    return (static_cast<std::uint16_t>(a) & static_cast<std::uint16_t>(b)) != 0;
}

enum class Error : std::int8_t {
    InvalidMagic    = -1,
    CrcMismatch     = -2,
    VersionGap      = -3,
    OutOfRange      = -4,
    ReadOnly        = -5,
    NotFound        = -6,
    BufferTooSmall  = -7,
    FlashWriteFault = -8,
    TrialActive     = -9,
    DependencyFault = -10
};

struct [[gnu::packed]] Header {
    std::uint32_t magic;
    std::uint16_t schema_version;
    std::uint16_t flags;
    std::uint32_t sequence_number;
    std::uint16_t payload_len;
    std::uint16_t reserved;
    std::uint32_t crc32;
};

template <typename T>
struct ParameterDescriptor {
    std::uint16_t key_id;
    std::string_view key_name;
    Type type;
    std::size_t offset_in_struct;
    Flags flags;
    T min_value;
    T max_value;
    T default_value;
    bool (*custom_validator)(const T &val) noexcept = nullptr;
};

} // namespace embedded::config
