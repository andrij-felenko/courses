#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span >
#include <chrono>
#include <expected>
#include <memory>
#include <cstring>
#include <openssl/hmac.h>
#include <openssl/evp.h>

namespace vwr {

enum class ValidationError {
    InvalidFormat,
    Base64DecodeFailed,
    HmacMismatch,
    EventIdMismatch,
    TokenExpired
};

struct TokenPayload {
    std::string customer_id;
    std::string event_id;
    int64_t exp{0};
};

class Gatekeeper {
public:
    explicit Gatekeeper(std::string secret_key) : secret_key_(std::move(secret_key)) {}

    [[nodiscard]] std::expected<TokenPayload, ValidationError> validate_token(
        std::string_view token_str,
        std::string_view expected_event_id) const 
    {
        const auto dot_pos = token_str.find('.');
        if (dot_pos == std::string_view::npos || dot_pos == 0 || dot_pos == token_str.length() - 1) {
            return std::unexpected(ValidationError::InvalidFormat);
        }

        const auto payload_b64 = token_str.substr(0, dot_pos);
        const auto sig_b64 = token_str.substr(dot_pos + 1);

        // 1. Обчислення HMAC-SHA256 для Base64URL-версії payload
        unsigned char expected_hmac[EVP_MAX_MD_SIZE];
        unsigned int hmac_len = 0;

        HMAC(EVP_sha256(),
             secret_key_.data(), static_cast<int>(secret_key_.size()),
             reinterpret_cast<const unsigned char*>(payload_b64.data()), payload_b64.size(),
             expected_hmac, &hmac_len);

        // 2. Декодування переданого підпису
        auto provided_hmac_res = base64url_decode(sig_b64);
        if (!provided_hmac_res) {
            return std::unexpected(ValidationError::Base64DecodeFailed);
        }

        if (provided_hmac_res->size() != hmac_len) {
            return std::unexpected(ValidationError::HmacMismatch);
        }

        // 3. Порівняння у константному часі
        if (!constant_time_compare(
                std::span<const unsigned char>(expected_hmac, hmac_len),
                std::span<const unsigned char>(*provided_hmac_res))) 
        {
            return std::unexpected(ValidationError::HmacMismatch);
        }

        // 4. Декодування та розбір тіла payload
        auto decoded_payload_raw = base64url_decode(payload_b64);
        if (!decoded_payload_raw) {
            return std::unexpected(ValidationError::Base64DecodeFailed);
        }

        std::string_view payload_str(
            reinterpret_cast<const char*>(decoded_payload_raw->data()),
            decoded_payload_raw->size());

        auto payload_res = parse_payload(payload_str);
        if (!payload_res) {
            return std::unexpected(ValidationError::InvalidFormat);
        }

        // 5. Перевірка бізнес-інваріантів
        if (payload_res->event_id != expected_event_id) {
            return std::unexpected(ValidationError::EventIdMismatch);
        }

        const auto now = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()).count();

        if (now > payload_res->exp) {
            return std::unexpected(ValidationError::TokenExpired);
        }

        return *payload_res;
    }

private:
    std::string secret_key_;

    static bool constant_time_compare(
        std::span<const unsigned char> a,
        std::span<const unsigned char> b) noexcept 
    {
        if (a.size() != b.size()) return false;
        unsigned char result = 0;
        for (size_t i = 0; i < a.size(); ++i) {
            result |= (a[i] ^ b[i]);
        }
        return result == 0;
    }

    static std::optional<std::vector<unsigned char>> base64url_decode(std::string_view input) {
        std::string s(input);
        for (char &c : s) {
            if (c == '-') c = '+';
            else if (c == '_') c = '/';
        }
        while (s.size() % 4 != 0) {
            s.push_back('=');
        }

        std::vector<unsigned char> out(s.size());
        auto bio = ::BIO_new_mem_buf(s.data(), static_cast<int>(s.size()));
        auto b64 = ::BIO_new(::BIO_f_base64());
        bio = ::BIO_push(b64, bio);
        ::BIO_set_flags(bio, BIO_FLAGS_BASE64_NO_NL);

        int len = ::BIO_read(bio, out.data(), static_cast<int>(out.size()));
        ::BIO_free_all(bio);

        if (len < 0) return std::nullopt;
        out.resize(static_cast<size_t>(len));
        return out;
    }

    static std::optional<TokenPayload> parse_payload(std::string_view s) {
        TokenPayload p;
        size_t first = s.find(':');
        size_t second = s.find(':', first + 1);
        if (first == std::string_view::npos || second == std::string_view::npos) {
            return std::nullopt;
        }

        p.customer_id = std::string(s.substr(0, first));
        p.event_id = std::string(s.substr(first + 1, second - (first + 1)));
        try {
            p.exp = std::stoll(std::string(s.substr(second + 1)));
        } catch (...) {
            return std::nullopt;
        }
        return p;
    }
};

} // namespace vwr
