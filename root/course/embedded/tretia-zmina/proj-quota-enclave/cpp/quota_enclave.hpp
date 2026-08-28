// quota_enclave.hpp — Типобезпечний рушій квотування на C++20
#pragma once

#include <array>
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <vector>
#include <expected>
#include <chrono>
#include <algorithm>

namespace manufacturing {

inline constexpr size_t kSignatureLen = 64;
inline constexpr size_t kKeyLen       = 32;
inline constexpr size_t kUidLen       = 12;
inline constexpr uint32_t kTicketMagic = 0x544B4554; // 'TKET'

enum class ProvError {
    InvalidSignature,
    Expired,
    WrongStation,
    QuotaExhausted,
    StorageFailure,
    InvalidArgument
};

#pragma pack(push, 1)
struct OemTicket {
    uint32_t magic{kTicketMagic};
    uint32_t batch_id{0};
    uint32_t model_id{0};
    uint32_t station_id{0};
    uint32_t quota_total{0};
    uint64_t valid_from_ts{0};
    uint64_t valid_until_ts{0};
    std::array<uint8_t, kSignatureLen> oem_signature{};
};

struct AuditRecord {
    uint32_t record_seq{0};
    uint32_t batch_id{0};
    std::array<uint8_t, kUidLen> silicon_uid{};
    std::array<uint8_t, kKeyLen> device_pubkey{};
    uint64_t timestamp{0};
};
#pragma pack(pop)

class QuotaEnclave {
public:
    explicit QuotaEnclave(uint32_t station_id, std::span<const uint8_t, kKeyLen> oem_root_pubkey)
        : station_id_(station_id) {
        std::copy(oem_root_pubkey.begin(), oem_root_pubkey.end(), oem_root_pubkey_.begin());
    }

    // Завантаження квитка замовника
    std::expected<void, ProvError> load_ticket(const OemTicket& ticket, uint64_t current_ts) noexcept {
        if (ticket.magic != kTicketMagic) {
            return std::unexpected(ProvError::InvalidArgument);
        }
        if (ticket.station_id != station_id_) {
            return std::unexpected(ProvError::WrongStation);
        }
        if (current_ts < ticket.valid_from_ts || current_ts > ticket.valid_until_ts) {
            return std::unexpected(ProvError::Expired);
        }

        // Перевірка підпису над тілом квитка
        const auto* raw_bytes = reinterpret_cast<const uint8_t*>(&ticket);
        constexpr size_t signed_size = offsetof(OemTicket, oem_signature);
        std::span<const uint8_t> signed_payload(raw_bytes, signed_size);

        if (!verify_signature(signed_payload, ticket.oem_signature)) {
            return std::unexpected(ProvError::InvalidSignature);
        }

        active_batch_id_ = ticket.batch_id;
        quota_remaining_ = ticket.quota_total;
        audit_log_.clear();
        return {};
    }

    // Провізіонування одного екземпляра
    std::expected<std::vector<uint8_t>, ProvError> provision_device(
        std::span<const uint8_t, kUidLen> silicon_uid,
        std::span<const uint8_t, kKeyLen> device_pubkey,
        uint64_t current_ts) {
        
        if (quota_remaining_ == 0) {
            return std::unexpected(ProvError::QuotaExhausted);
        }

        // 1. Атомарне списання ліміту перед підписом
        --quota_remaining_;

        // 2. Створення сертифіката пристрою
        std::vector<uint8_t> cert(kUidLen + kKeyLen);
        std::copy(silicon_uid.begin(), silicon_uid.end(), cert.begin());
        std::copy(device_pubkey.begin(), device_pubkey.end(), cert.begin() + kUidLen);

        // 3. Додавання запису до журналу аудиту
        AuditRecord rec{};
        rec.record_seq = static_cast<uint32_t>(audit_log_.size() + 1);
        rec.batch_id = active_batch_id_;
        rec.timestamp = current_ts;
        std::copy(silicon_uid.begin(), silicon_uid.end(), rec.silicon_uid.begin());
        std::copy(device_pubkey.begin(), device_pubkey.end(), rec.device_pubkey.begin());
        audit_log_.push_back(rec);

        return cert;
    }

    [[nodiscard]] uint32_t quota_remaining() const noexcept { return quota_remaining_; }
    [[nodiscard]] const std::vector<AuditRecord>& audit_log() const noexcept { return audit_log_; }

private:
    bool verify_signature(std::span<const uint8_t> payload,
                          std::span<const uint8_t, kSignatureLen> sig) const noexcept {
        // У продакшені: виклик libsodium crypto_sign_verify_detached
        (void)payload; (void)sig;
        return true;
    }

    uint32_t station_id_{0};
    uint32_t active_batch_id_{0};
    uint32_t quota_remaining_{0};
    std::array<uint8_t, kKeyLen> oem_root_pubkey_{};
    std::vector<AuditRecord> audit_log_{};
};

} // namespace manufacturing
