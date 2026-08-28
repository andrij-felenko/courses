#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <optional>
#include <span>
#include <sstream>
#include <iomanip>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>

class WebhookSecurityCpp {
public:
    struct Config {
        std::string primary_secret;
        std::optional<std::string> secondary_secret;
        std::chrono::seconds tolerance{300};
    };

    explicit WebhookSecurityCpp(Config cfg) : config_(std::move(cfg)) {}

    [[nodiscard]] bool verify(std::span<const uint8_t> raw_body, std::string_view sig_header) const {
        if (raw_body.empty() || sig_header.empty()) return false;

        int64_t timestamp = -1;
        std::vector<std::string> signatures;

        // Розбір заголовка: t=1719580800,v1=5257a869e7ec...
        std::stringstream ss{std::string(sig_header)};
        std::string item;
        while (std::getline(ss, item, ',')) {
            auto eq_pos = item.find('=');
            if (eq_pos == std::string::npos) continue;
            auto key = item.substr(0, eq_pos);
            auto val = item.substr(eq_pos + 1);

            // Очищення від пробілів
            while (!key.empty() && key.front() == ' ') key.erase(0, 1);
            while (!key.empty() && key.back() == ' ') key.pop_back();
            while (!val.empty() && val.front() == ' ') val.erase(0, 1);
            while (!val.empty() && val.back() == ' ') val.pop_back();

            if (key == "t") {
                try { timestamp = std::stoll(val); } catch (...) { return false; }
            } else if (key == "v1") {
                signatures.push_back(val);
            }
        }

        if (timestamp == -1 || signatures.empty()) return false;

        // 1. Перевірка часового вікна
        const auto now = std::chrono::duration_cast<std::chrono::seconds>(
            std::chrono::system_clock::now().time_since_epoch()
        ).count();

        if (std::abs(now - timestamp) > config_.tolerance.count()) {
            return false;
        }

        // 2. Побудова буфера підпису: timestamp || "." || raw_body
        std::string prefix = std::to_string(timestamp) + ".";
        std::vector<uint8_t> signed_payload(prefix.begin(), prefix.end());
        signed_payload.insert(signed_payload.end(), raw_body.begin(), raw_body.end());

        std::vector<std::string> active_secrets{config_.primary_secret};
        if (config_.secondary_secret.has_value()) {
            active_secrets.push_back(*config_.secondary_secret);
        }

        // 3. Перевірка підпису проти активних ключів
        for (const auto& secret : active_secrets) {
            unsigned char hmac_buf[SHA256_DIGEST_LENGTH];
            unsigned int hmac_len = 0;

            HMAC(EVP_sha256(),
                 secret.data(), static_cast<int>(secret.size()),
                 signed_payload.data(), signed_payload.size(),
                 hmac_buf, &hmac_len);

            std::stringstream hex_stream;
            for (unsigned int i = 0; i < hmac_len; ++i) {
                hex_stream << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(hmac_buf[i]);
            }
            std::string expected_hex = hex_stream.str();

            for (const auto& sig : signatures) {
                // 4. Порівняння сталого часу (Constant-Time Verification)
                if (sig.size() == expected_hex.size() &&
                    CRYPTO_memcmp(sig.data(), expected_hex.data(), sig.size()) == 0) {
                    return true;
                }
            }
        }

        return false;
    }

private:
    Config config_;
};
