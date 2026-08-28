#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>
#include <array>
#include <variant>
#include <optional>
#include <system_error>
#include <cstring>

namespace cbor {

enum class Error {
    Ok = 0,
    BufferOverflow,
    UnexpectedEof,
    InvalidHeader,
    UnsupportedType
};

struct ErrorCategory : std::error_category {
    const char* name() const noexcept override { return "cbor"; }
    std::string message(int ev) const override {
        switch (static_cast<Error>(ev)) {
            case Error::BufferOverflow: return "Buffer overflow";
            case Error::UnexpectedEof: return "Unexpected end of buffer";
            case Error::InvalidHeader: return "Invalid header byte";
            case Error::UnsupportedType: return "Unsupported major type";
            default: return "Success";
        }
    }
};

inline const std::error_category& error_category() {
    static ErrorCategory cat;
    return cat;
}

inline std::error_code make_error_code(Error e) {
    return {static_cast<int>(e), error_category()};
}

enum class MajorType : uint8_t {
    UnsignedInt = 0,
    NegativeInt = 1,
    ByteString  = 2,
    TextString  = 3,
    Array       = 4,
    Map         = 5,
    Tag         = 6,
    Simple      = 7
};

struct ArrayHeader { size_t count; };
struct MapHeader   { size_t pairs_count; };
struct TagHeader   { uint64_t tag_id; };
struct NullValue   {};

using Value = std::variant<
    uint64_t,
    int64_t,
    std::span<const uint8_t>,
    std::string_view,
    ArrayHeader,
    MapHeader,
    TagHeader,
    bool,
    NullValue,
    float,
    double
>;

class Reader {
public:
    explicit constexpr Reader(std::span<const uint8_t> buffer) noexcept
        : buf_(buffer), offset_(0) {}

    [[nodiscard]] size_t remaining() const noexcept { return buf_.size() - offset_; }
    [[nodiscard]] size_t offset() const noexcept { return offset_; }

    [[nodiscard]] std::span<const uint8_t> current_slice() const noexcept {
        return buf_.subspan(offset_);
    }

private:
    std::span<const uint8_t> buf_;
    size_t offset_;
    friend class Decoder;
};

class Writer {
public:
    explicit constexpr Writer(std::span<uint8_t> buffer) noexcept
        : buf_(buffer), offset_(0) {}

    [[nodiscard]] size_t written_size() const noexcept { return offset_; }
    [[nodiscard]] size_t remaining_capacity() const noexcept { return buf_.size() - offset_; }
    [[nodiscard]] std::span<const uint8_t> written_data() const noexcept {
        return buf_.first(offset_);
    }

private:
    std::span<uint8_t> buf_;
    size_t offset_;
    friend class Encoder;
};

} // namespace cbor
