#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <algorithm>

namespace daplink::diagnostics {

enum class SenseKey : std::uint8_t {
    NoSense        = 0x00U,
    MediumError    = 0x03U,
    IllegalRequest = 0x05U
};

enum class AdditionalSenseCode : std::uint8_t {
    None               = 0x00U,
    WriteError         = 0x0CU,
    InvalidFieldInCdb  = 0x24U,
    WriteProtected     = 0x27U
};

enum class FailureReason : std::uint8_t {
    None,
    FlashTimeout,
    VerifyMismatch,
    VectorInvalid,
    WriteProtected
};

struct DiagnosticRecord {
    FailureReason reason{FailureReason::None};
    std::uintptr_t faultAddress{0};
    std::uint32_t expectedValue{0};
    std::uint32_t actualValue{0};
};

class ErrorReporter {
public:
    void record(FailureReason reason, std::uintptr_t addr = 0,
                std::uint32_t expected = 0, std::uint32_t actual = 0) noexcept {
        m_record = {reason, addr, expected, actual};
    }

    [[nodiscard]] std::size_t buildSenseData(std::span<std::uint8_t> buffer) const noexcept {
        if (buffer.size() < 18U) {
            return 0U;
        }
        std::fill(buffer.begin(), buffer.begin() + 18U, 0U);
        buffer[0] = 0x70U;
        buffer[7] = 10U;

        switch (m_record.reason) {
        case FailureReason::FlashTimeout:
        case FailureReason::VerifyMismatch:
            buffer[2] = static_cast<std::uint8_t>(SenseKey::MediumError);
            buffer[12] = static_cast<std::uint8_t>(AdditionalSenseCode::WriteError);
            buffer[13] = 0x00U;
            break;
        case FailureReason::WriteProtected:
            buffer[2] = static_cast<std::uint8_t>(SenseKey::IllegalRequest);
            buffer[12] = static_cast<std::uint8_t>(AdditionalSenseCode::WriteProtected);
            buffer[13] = 0x00U;
            break;
        case FailureReason::VectorInvalid:
            buffer[2] = static_cast<std::uint8_t>(SenseKey::IllegalRequest);
            buffer[12] = static_cast<std::uint8_t>(AdditionalSenseCode::InvalidFieldInCdb);
            buffer[13] = 0x00U;
            break;
        default:
            buffer[2] = static_cast<std::uint8_t>(SenseKey::NoSense);
            buffer[12] = static_cast<std::uint8_t>(AdditionalSenseCode::None);
            buffer[13] = 0x00U;
            break;
        }
        return 18U;
    }

    void synthesizeFailTxt(std::span<std::uint8_t, 512> sector) const noexcept {
        std::fill(sector.begin(), sector.end(), static_cast<std::uint8_t>(' '));
        std::string_view msgText;

        switch (m_record.reason) {
        case FailureReason::FlashTimeout:
            msgText = "error: An error occurred.

reason: Flash erase/programming timeout.

";
            break;
        case FailureReason::VerifyMismatch:
            msgText = "error: An error occurred.

reason: Verification mismatch in Flash cells.

";
            break;
        case FailureReason::VectorInvalid:
            msgText = "error: An error occurred.

reason: Table of vectors is corrupted or invalid.

";
            break;
        case FailureReason::WriteProtected:
            msgText = "error: An error occurred.

reason: Memory sector is write-protected.

";
            break;
        default:
            msgText = "error: An error occurred.

reason: Unspecified failure.

";
            break;
        }

        std::copy(msgText.begin(), msgText.end(), sector.begin());
    }

    [[nodiscard]] static bool isFirmwareImage(std::string_view filename83) noexcept {
        if (filename83.size() < 11U || filename83[0] == '.' || filename83[0] == 'å') {
            return false;
        }
        const auto ext = filename83.substr(8, 3);
        return (ext == "BIN" || ext == "HEX");
    }

private:
    DiagnosticRecord m_record{};
};

} // namespace daplink::diagnostics
