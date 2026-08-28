#include <cstddef>
#include <cstdint>
#include <cstring>
#include <expected>
#include <span>
#include <system_error>
#include <array>

namespace security {

inline constexpr size_t kMaxPayloadLen = 1024;

struct SafeMessage {
    uint32_t length{0};
    std::array<uint8_t, kMaxPayloadLen> data{};
};

enum class BoundaryError {
    NullSource,
    InvalidSize,
    PayloadLengthOverflow,
    BufferTruncated
};

class [[nodiscard]] BoundaryBufferValidator {
public:
    static std::expected<SafeMessage, BoundaryError> fetch_and_validate(std::span<const uint8_t> untrusted_raw) noexcept {
        if (untrusted_raw.empty()) {
            return std::unexpected(BoundaryError::NullSource);
        }
        if (untrusted_raw.size() < sizeof(uint32_t) || untrusted_raw.size() > sizeof(SafeMessage)) {
            return std::unexpected(BoundaryError::InvalidSize);
        }

        // Крок 1: Єдине копіювання у локальний фрейм
        SafeMessage local_copy{};
        std::memcpy(&local_copy, untrusted_raw.data(), untrusted_raw.size());

        // Крок 2: Валідація локальної копії
        if (local_copy.length > kMaxPayloadLen) {
            return std::unexpected(BoundaryError::PayloadLengthOverflow);
        }
        if (sizeof(uint32_t) + local_copy.length > untrusted_raw.size()) {
            return std::unexpected(BoundaryError::BufferTruncated);
        }

        return local_copy;
    }
};

} // namespace security
