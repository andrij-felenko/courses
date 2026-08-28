#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <expected>
#include <chrono>
#include <memory>
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"

enum class TrustSlotState : uint8_t {
    Empty   = 0xFF,
    Standby = 0x02,
    Active  = 0x01,
    Revoked = 0x00
};

enum class TrustStoreError {
    InvalidMagic,
    InactiveSlot,
    InvalidLength,
    ChecksumMismatch,
    ExpiredCertificate,
    MbedTlsParseError,
    NoValidAnchors
};

struct alignas(4) TrustSlotHeader {
    uint32_t magic;
    uint16_t version;
    TrustSlotState slot_state;
    uint8_t  reserved;
    uint32_t cert_len;
    uint64_t valid_from;
    uint64_t valid_to;
    uint32_t data_crc32;
    uint8_t  padding[36];
};

class DualTrustStore {
public:
    static constexpr uint32_t ExpectedMagic = 0x54525553U;
    static constexpr size_t MaxCertSize = 2048U;

    explicit DualTrustStore(std::chrono::system_clock::time_point now) noexcept
        : currentTimeSec_(std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count()) {
        mbedtls_x509_crt_init(&caChain_);
    }

    ~DualTrustStore() noexcept {
        mbedtls_x509_crt_free(&caChain_);
    }

    DualTrustStore(const DualTrustStore&) = delete;
    DualTrustStore& operator=(const DualTrustStore&) = delete;
    DualTrustStore(DualTrustStore&&) = delete;
    DualTrustStore& operator=(DualTrustStore&&) = delete;

    [[nodiscard]] std::expected<void, TrustStoreError> loadSlot(
        const TrustSlotHeader& header,
        std::span<const uint8_t> certData) noexcept {
        
        if (header.magic != ExpectedMagic) {
            return std::unexpected(TrustStoreError::InvalidMagic);
        }
        if (header.slot_state != TrustSlotState::Active && header.slot_state != TrustSlotState::Standby) {
            return std::unexpected(TrustStoreError::InactiveSlot);
        }
        if (header.cert_len == 0 || header.cert_len > certData.size() || header.cert_len > MaxCertSize) {
            return std::unexpected(TrustStoreError::InvalidLength);
        }

        if (calculateCrc32(certData.subspan(0, header.cert_len)) != header.data_crc32) {
            return std::unexpected(TrustStoreError::ChecksumMismatch);
        }

        if (currentTimeSec_ > 0) {
            if (currentTimeSec_ < header.valid_from || currentTimeSec_ > header.valid_to) {
                if (header.slot_state == TrustSlotState::Active) {
                    return std::unexpected(TrustStoreError::ExpiredCertificate);
                }
            }
        }

        const int ret = mbedtls_x509_crt_parse(&caChain_, certData.data(), header.cert_len);
        if (ret != 0) {
            return std::unexpected(TrustStoreError::MbedTlsParseError);
        }

        loadedAnchorsCount_++;
        return {};
    }

    [[nodiscard]] mbedtls_x509_crt* nativeHandle() noexcept {
        return &caChain_;
    }

    [[nodiscard]] size_t anchorsCount() const noexcept {
        return loadedAnchorsCount_;
    }

private:
    mbedtls_x509_crt caChain_{};
    size_t loadedAnchorsCount_{0};
    uint64_t currentTimeSec_{0};

    [[nodiscard]] static uint32_t calculateCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (const uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
            }
        }
        return ~crc;
    }
};
