// C++ Implementation: Idiomatic C++20 Thread-Safe Revocation Engine
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_set>
#include <vector>
#include <optional>
#include <shared_mutex>
#include <atomic>
#include <chrono>
#include <expected>

namespace dh::security {

enum class RevocationError {
    Expired,
    IssuedBeforeLeak,
    BlacklistedJti,
    UnknownKeyId,
    SignatureInvalid
};

struct JwtClaims {
    std::string kid;
    std::string jti;
    uint64_t user_id;
    uint64_t issued_at;
    uint64_t expires_at;
};

struct KeyEntry {
    std::string kid;
    std::string public_key_pem;
    bool active_for_signing{false};
    uint64_t created_at{0};
};

class RevocationEngine {
public:
    RevocationEngine() = default;

    void trigger_global_leak_emergency(uint64_t leak_time_epoch) noexcept {
        leak_timestamp_.store(leak_time_epoch, std::memory_order_release);
    }

    void blacklist_jti(std::string_view jti) {
        std::unique_lock lock(mutex_);
        blacklisted_jtis_.emplace(jti);
    }

    void register_key(KeyEntry key) {
        std::unique_lock lock(mutex_);
        if (key.active_for_signing) {
            for (auto& k : key_ring_) {
                k.active_for_signing = false;
            }
        }
        key_ring_.push_back(std::move(key));
    }

    [[nodiscard]] std::expected<void, RevocationError> validate_jwt(
        const JwtClaims& claims,
        uint64_t current_time
    ) const {
        if (current_time >= claims.expires_at) {
            return std::unexpected(RevocationError::Expired);
        }

        const uint64_t global_leak = leak_timestamp_.load(std::memory_order_acquire);
        if (global_leak > 0 && claims.issued_at <= global_leak) {
            return std::unexpected(RevocationError::IssuedBeforeLeak);
        }

        std::shared_lock lock(mutex_);

        // 1. Verify Key ID (kid) exists in JWKS Key Ring
        bool kid_exists = false;
        for (const auto& key : key_ring_) {
            if (key.kid == claims.kid) {
                kid_exists = true;
                break;
            }
        }
        if (!kid_exists) {
            return std::unexpected(RevocationError::UnknownKeyId);
        }

        // 2. Check JTI Blacklist
        if (blacklisted_jtis_.contains(claims.jti)) {
            return std::unexpected(RevocationError::BlacklistedJti);
        }

        return {};
    }

    [[nodiscard]] std::optional<KeyEntry> get_signing_key() const {
        std::shared_lock lock(mutex_);
        for (const auto& key : key_ring_) {
            if (key.active_for_signing) {
                return key;
            }
        }
        return std::nullopt;
    }

private:
    std::atomic<uint64_t> leak_timestamp_{0};
    mutable std::shared_mutex mutex_;
    std::unordered_set<std::string> blacklisted_jtis_;
    std::vector<KeyEntry> key_ring_;
};

} // namespace dh::security
