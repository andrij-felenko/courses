#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <string_view>
#include <chrono>
#include <memory>
#include <optional>
#include <algorithm>
#include <openssl/hmac.h>
#include <openssl/rand.h>

namespace crypto_auth {

inline constexpr size_t NonceSize = 16;
inline constexpr size_t HmacSize = 32;
inline constexpr std::chrono::seconds MaxChallengeAge{30};
inline constexpr size_t ReplayCacheCapacity = 256;

#pragma pack(push, 1)
struct ChallengeToken {
    std::array<uint8_t, NonceSize> nonce{};
    uint64_t timestamp_sec{0};
    std::array<uint8_t, HmacSize> server_mac{};
};

struct AuthResponse {
    uint32_t client_id{0};
    std::array<uint8_t, HmacSize> response_mac{};
};
#pragma pack(pop)

enum class VerifyError {
    InternalError,
    InvalidServerMac,
    ExpiredTimestamp,
    ReplayDetected,
    InvalidClientProof
};

/* Порівняння масивів за сталий час для запобігання Timing Attacks */
[[nodiscard]] bool constant_time_equal(std::span<const uint8_t> a,
                                       std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

/* Обчислення HMAC-SHA256 */
[[nodiscard]] std::optional<std::array<uint8_t, HmacSize>>
compute_hmac(std::span<const uint8_t> key, std::span<const uint8_t> data) noexcept {
    std::array<uint8_t, HmacSize> result{};
    unsigned int len = 0;
    if (!HMAC(EVP_sha256(), key.data(), static_cast<int>(key.size()),
              data.data(), data.size(), result.data(), &len)) {
        return std::nullopt;
    }
    return result;
}

class ReplayCache {
public:
    [[nodiscard]] bool test_and_add(const std::array<uint8_t, NonceSize>& nonce) noexcept {
        auto it = std::find_if(cache_.begin(), cache_.end(), [&](const auto& entry) {
            return constant_time_equal(entry, nonce);
        });
        if (it != cache_.end()) {
            return false; /* Знайдено дублікат у вікні свіжості */
        }
        if (cache_.size() >= ReplayCacheCapacity) {
            cache_.erase(cache_.begin());
        }
        cache_.push_back(nonce);
        return true;
    }
private:
    std::vector<std::array<uint8_t, NonceSize>> cache_;
};

class AuthServer {
public:
    explicit AuthServer(std::vector<uint8_t> server_key)
        : server_key_(std::move(server_key)) {}

    [[nodiscard]] std::optional<ChallengeToken>
    create_challenge(uint32_t client_id) const noexcept {
        ChallengeToken token;
        if (RAND_bytes(token.nonce.data(), static_cast<int>(token.nonce.size())) != 1) {
            return std::nullopt;
        }

        const auto now = std::chrono::system_clock::now();
        token.timestamp_sec = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count()
        );

        std::vector<uint8_t> sign_payload;
        sign_payload.reserve(NonceSize + sizeof(uint64_t) + sizeof(uint32_t));
        sign_payload.insert(sign_payload.end(), token.nonce.begin(), token.nonce.end());

        const auto* ts_bytes = reinterpret_cast<const uint8_t*>(&token.timestamp_sec);
        sign_payload.insert(sign_payload.end(), ts_bytes, ts_bytes + sizeof(uint64_t));

        const auto* id_bytes = reinterpret_cast<const uint8_t*>(&client_id);
        sign_payload.insert(sign_payload.end(), id_bytes, id_bytes + sizeof(uint32_t));

        auto mac = compute_hmac(server_key_, sign_payload);
        if (!mac) return std::nullopt;
        token.server_mac = *mac;
        return token;
    }

    [[nodiscard]] std::optional<VerifyError>
    verify_response(const ChallengeToken& token,
                    const AuthResponse& resp,
                    std::span<const uint8_t> client_secret,
                    std::string_view expected_action) noexcept {
        /* 1. Перевірка валідності талона сервера */
        std::vector<uint8_t> sign_payload;
        sign_payload.reserve(NonceSize + sizeof(uint64_t) + sizeof(uint32_t));
        sign_payload.insert(sign_payload.end(), token.nonce.begin(), token.nonce.end());
        const auto* ts_bytes = reinterpret_cast<const uint8_t*>(&token.timestamp_sec);
        sign_payload.insert(sign_payload.end(), ts_bytes, ts_bytes + sizeof(uint64_t));
        const auto* id_bytes = reinterpret_cast<const uint8_t*>(&resp.client_id);
        sign_payload.insert(sign_payload.end(), id_bytes, id_bytes + sizeof(uint32_t));

        auto expected_srv_mac = compute_hmac(server_key_, sign_payload);
        if (!expected_srv_mac || !constant_time_equal(token.server_mac, *expected_srv_mac)) {
            return VerifyError::InvalidServerMac;
        }

        /* 2. Перевірка вікна життя талона */
        const auto now_sec = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::seconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count()
        );
        if (now_sec < token.timestamp_sec || (now_sec - token.timestamp_sec) > MaxChallengeAge.count()) {
            return VerifyError::ExpiredTimestamp;
        }

        /* 3. Перевірка на повторне використання */
        if (!replay_cache_.test_and_add(token.nonce)) {
            return VerifyError::ReplayDetected;
        }

        /* 4. Перевірка доказу володіння клієнтським секретом */
        std::vector<uint8_t> client_payload;
        const auto* tok_ptr = reinterpret_cast<const uint8_t*>(&token);
        client_payload.insert(client_payload.end(), tok_ptr, tok_ptr + sizeof(ChallengeToken));
        client_payload.insert(client_payload.end(), expected_action.begin(), expected_action.end());

        auto expected_client_mac = compute_hmac(client_secret, client_payload);
        if (!expected_client_mac || !constant_time_equal(resp.response_mac, *expected_client_mac)) {
            return VerifyError::InvalidClientProof;
        }

        return std::nullopt; /* Успішна валідація */
    }

private:
    std::vector<uint8_t> server_key_;
    ReplayCache replay_cache_;
};

class AuthClient {
public:
    [[nodiscard]] static std::optional<AuthResponse>
    compute_response(uint32_t client_id,
                     std::span<const uint8_t> client_secret,
                     const ChallengeToken& token,
                     std::string_view action_context) noexcept {
        std::vector<uint8_t> payload;
        const auto* tok_ptr = reinterpret_cast<const uint8_t*>(&token);
        payload.insert(payload.end(), tok_ptr, tok_ptr + sizeof(ChallengeToken));
        payload.insert(payload.end(), action_context.begin(), action_context.end());

        auto mac = compute_hmac(client_secret, payload);
        if (!mac) return std::nullopt;

        AuthResponse resp;
        resp.client_id = client_id;
        resp.response_mac = *mac;
        return resp;
    }
};

} // namespace crypto_auth
