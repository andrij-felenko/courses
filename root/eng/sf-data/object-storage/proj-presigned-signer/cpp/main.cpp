#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <span>
#include <expected>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>

class SigV4Signer {
public:
    struct Credentials {
        std::string access_key;
        std::string secret_key;
        std::string region;
        std::string service{"s3"};
    };

    enum class Error {
        Expired,
        SignatureMismatch,
        InvalidFormat
    };

    explicit SigV4Signer(Credentials creds) : creds_(std::move(creds)) {}

    ~SigV4Signer() {
        // Очищення секретного ключа в оперативній пам'яті при знищенні об'єкта
        OPENSSL_cleanse(creds_.secret_key.data(), creds_.secret_key.size());
    }

    [[nodiscard]] std::string generate_presigned_url(
        std::string_view http_method,
        std::string_view host,
        std::string_view uri,
        std::chrono::seconds expires,
        std::chrono::system_clock::time_point now = std::chrono::system_clock::now()) const
    {
        const auto [date_stamp, amz_date] = format_timestamps(now);
        const std::string credential_scope = date_stamp + "/" + creds_.region + "/" + creds_.service + "/aws4_request";
        const std::string credential_encoded = creds_.access_key + "%2F" + date_stamp + "%2F" + creds_.region + "%2F" + creds_.service + "%2Faws4_request";

        const std::string canonical_qs =
            "X-Amz-Algorithm=AWS4-HMAC-SHA256"
            "&X-Amz-Credential=" + credential_encoded +
            "&X-Amz-Date=" + amz_date +
            "&X-Amz-Expires=" + std::to_string(expires.count()) +
            "&X-Amz-SignedHeaders=host";

        const std::string canonical_headers = "host:" + std::string(host) + "\n";
        const std::string canonical_req = std::string(http_method) + "\n" +
                                          std::string(uri) + "\n" +
                                          canonical_qs + "\n" +
                                          canonical_headers + "\n" +
                                          "host\n" +
                                          "UNSIGNED-PAYLOAD";

        const std::string canonical_req_hash = sha256_hex(canonical_req);
        const std::string string_to_sign = "AWS4-HMAC-SHA256\n" + amz_date + "\n" + credential_scope + "\n" + canonical_req_hash;

        const auto k_signing = derive_signing_key(creds_.secret_key, date_stamp, creds_.region, creds_.service);
        const auto signature = hmac_sha256_hex(k_signing, string_to_sign);

        return "https://" + std::string(host) + std::string(uri) + "?" + canonical_qs + "&X-Amz-Signature=" + signature;
    }

    [[nodiscard]] std::expected<void, Error> validate_presigned_url(
        std::string_view http_method,
        std::string_view host,
        std::string_view uri,
        std::string_view canonical_qs_no_sig,
        std::string_view provided_sig,
        std::string_view amz_date,
        std::string_view date_stamp,
        std::chrono::system_clock::time_point req_time,
        std::chrono::seconds expires,
        std::chrono::system_clock::time_point current_time = std::chrono::system_clock::now()) const
    {
        if (current_time < req_time || current_time > (req_time + expires)) {
            return std::unexpected(Error::Expired);
        }

        const std::string credential_scope = std::string(date_stamp) + "/" + creds_.region + "/" + creds_.service + "/aws4_request";
        const std::string canonical_headers = "host:" + std::string(host) + "\n";
        const std::string canonical_req = std::string(http_method) + "\n" +
                                          std::string(uri) + "\n" +
                                          std::string(canonical_qs_no_sig) + "\n" +
                                          canonical_headers + "\n" +
                                          "host\n" +
                                          "UNSIGNED-PAYLOAD";

        const std::string canonical_req_hash = sha256_hex(canonical_req);
        const std::string string_to_sign = "AWS4-HMAC-SHA256\n" + std::string(amz_date) + "\n" + credential_scope + "\n" + canonical_req_hash;

        const auto k_signing = derive_signing_key(creds_.secret_key, date_stamp, creds_.region, creds_.service);
        const auto expected_sig = hmac_sha256_hex(k_signing, string_to_sign);

        if (provided_sig.size() != 64 ||
            CRYPTO_memcmp(provided_sig.data(), expected_sig.data(), 64) != 0) {
            return std::unexpected(Error::SignatureMismatch);
        }

        return {};
    }

private:
    Credentials creds_;

    static std::string sha256_hex(std::string_view input) {
        std::array<unsigned char, SHA256_DIGEST_LENGTH> hash{};
        SHA256(reinterpret_cast<const unsigned char*>(input.data()), input.size(), hash.data());
        return bytes_to_hex(hash);
    }

    static std::array<unsigned char, SHA256_DIGEST_LENGTH> hmac_sha256_raw(
        std::span<const unsigned char> key, std::string_view data)
    {
        std::array<unsigned char, SHA256_DIGEST_LENGTH> out{};
        unsigned int len = SHA256_DIGEST_LENGTH;
        HMAC(EVP_sha256(), key.data(), static_cast<int>(key.size()),
             reinterpret_cast<const unsigned char*>(data.data()), data.size(), out.data(), &len);
        return out;
    }

    static std::string hmac_sha256_hex(std::span<const unsigned char> key, std::string_view data) {
        return bytes_to_hex(hmac_sha256_raw(key, data));
    }

    static std::array<unsigned char, SHA256_DIGEST_LENGTH> derive_signing_key(
        std::string_view secret, std::string_view date, std::string_view region, std::string_view service)
    {
        const std::string k_secret = "AWS4" + std::string(secret);
        auto k_date = hmac_sha256_raw(std::span{reinterpret_cast<const unsigned char*>(k_secret.data()), k_secret.size()}, date);
        auto k_region = hmac_sha256_raw(k_date, region);
        auto k_service = hmac_sha256_raw(k_region, service);
        auto k_signing = hmac_sha256_raw(k_service, "aws4_request");

        OPENSSL_cleanse(k_date.data(), k_date.size());
        OPENSSL_cleanse(k_region.data(), k_region.size());
        OPENSSL_cleanse(k_service.data(), k_service.size());
        return k_signing;
    }

    static std::string bytes_to_hex(std::span<const unsigned char> bytes) {
        std::ostringstream oss;
        oss << std::hex << std::setfill('0');
        for (auto b : bytes) {
            oss << std::setw(2) << static_cast<int>(b);
        }
        return oss.str();
    }

    static std::pair<std::string, std::string> format_timestamps(std::chrono::system_clock::time_point tp) {
        const auto time_t_val = std::chrono::system_clock::to_time_t(tp);
        std::tm gm_tm{};
        #ifdef _WIN32
        gmtime_s(&gm_tm, &time_t_val);
        #else
        gmtime_r(&time_t_val, &gm_tm);
        #endif
        char d_buf[9], dt_buf[17];
        std::strftime(d_buf, sizeof(d_buf), "%Y%m%d", &gm_tm);
        std::strftime(dt_buf, sizeof(dt_buf), "%Y%m%dT%H%M%SZ", &gm_tm);
        return {std::string(d_buf), std::string(dt_buf)};
    }
};
