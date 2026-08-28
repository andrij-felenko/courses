#include <cstdint>
#include <cstddef>
#include <system_error>
#include <expected>
#include <span>
#include <memory>
#include <concepts>
#include <string_view>

namespace universal_hashing {

enum class ErrorCode {
    Success = 0,
    InvalidParameter,
    EntropyFailure,
    OutOfRange,
    BadAlignment
};

class UniversalHashCategory : public std::error_category {
public:
    [[nodiscard]] const char* name() const noexcept override {
        return "universal_hashing";
    }
    [[nodiscard]] std::string message(int ev) const override {
        switch (static_cast<ErrorCode>(ev)) {
            case ErrorCode::Success: return "Success";
            case ErrorCode::InvalidParameter: return "Invalid parameter provided";
            case ErrorCode::EntropyFailure: return "Failed to acquire system entropy";
            case ErrorCode::OutOfRange: return "Key out of domain range";
            case ErrorCode::BadAlignment: return "Data buffer bad alignment";
            default: return "Unknown error";
        }
    }
};

inline const UniversalHashCategory& category() noexcept {
    static UniversalHashCategory cat;
    return cat;
}

inline std::error_code make_error_code(ErrorCode e) noexcept {
    return {static_cast<int>(e), category()};
}

enum class FamilyType {
    ModularP61,
    MultiplyShift,
    Tabulation64
};

struct Config {
    FamilyType family{FamilyType::MultiplyShift};
    uint64_t num_buckets{1024};
    uint64_t custom_seed{0};
    bool use_custom_seed{false};
};

class IUniversalHasher {
public:
    virtual ~IUniversalHasher() = default;

    [[nodiscard]] virtual uint64_t hash(uint64_t key) const noexcept = 0;
    [[nodiscard]] virtual uint64_t hash(std::span<const std::byte> data) const noexcept = 0;
    virtual std::error_code reseed() noexcept = 0;
    [[nodiscard]] virtual uint64_t num_buckets() const noexcept = 0;
};

using HasherPtr = std::unique_ptr<IUniversalHasher>;

[[nodiscard]] std::expected<HasherPtr, std::error_code> create_hasher(const Config& config) noexcept;

} // namespace universal_hashing
