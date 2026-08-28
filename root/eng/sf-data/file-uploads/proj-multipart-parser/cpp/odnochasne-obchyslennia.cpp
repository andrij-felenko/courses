#include <openssl/evp.h>
#include <memory>
#include <span>
#include <vector>
#include <cstdint>

class StreamingHasher {
public:
    StreamingHasher() : ctx_(EVP_MD_CTX_new(), &EVP_MD_CTX_free) {
        EVP_DigestInit_ex(ctx_.get(), EVP_sha256(), nullptr);
    }

    void update(std::span<const uint8_t> chunk) {
        EVP_DigestUpdate(ctx_.get(), chunk.data(), chunk.size());
    }

    std::vector<uint8_t> finalize() {
        std::vector<uint8_t> digest(EVP_MD_size(EVP_sha256()));
        unsigned int len = 0;
        EVP_DigestFinal_ex(ctx_.get(), digest.data(), &len);
        return digest;
    }

private:
    std::unique_ptr<EVP_MD_CTX, decltype(&EVP_MD_CTX_free)> ctx_;
};
