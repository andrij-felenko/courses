#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <iomanip>
#include <sstream>
#include <openssl/sha.h>

class LayerVerifier {
public:
    LayerVerifier() {
        SHA256_Init(&ctx_);
    }

    void update(std::span<const uint8_t> data) noexcept {
        SHA256_Update(&ctx_, data.data(), data.size());
        total_bytes_ += data.size();
    }

    [[nodiscard]] bool verify(std::string_view expected_digest) {
        std::vector<uint8_t> hash(SHA256_DIGEST_LENGTH);
        SHA256_Final(hash.data(), &ctx_);

        std::ostringstream oss;
        for (uint8_t byte : hash) {
            oss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte);
        }
        computed_hex_ = oss.str();

        std::string_view expected_hex = expected_digest;
        if (expected_hex.starts_with("sha256:")) {
            expected_hex.remove_prefix(7);
        }

        return computed_hex_ == expected_hex;
    }

    [[nodiscard]] std::string_view computed_hex() const noexcept {
        return computed_hex_;
    }

    [[nodiscard]] size_t total_bytes() const noexcept {
        return total_bytes_;
    }

private:
    SHA256_CTX ctx_{};
    size_t total_bytes_{0};
    std::string computed_hex_;
};
