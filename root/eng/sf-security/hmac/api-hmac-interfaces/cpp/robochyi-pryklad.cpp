#include <array>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <span>
#include <stdexcept>
#include <string_view>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/core_names.h>

namespace crypto {

class OpenSslHmac {
public:
    explicit OpenSslHmac(std::span<const uint8_t> key, std::string_view hash_name = "SHA256")
        : mac_(EVP_MAC_fetch(nullptr, "HMAC", nullptr), EVP_MAC_free),
          ctx_(nullptr, EVP_MAC_CTX_free)
    {
        if (!mac_) throw std::runtime_error("Не вдалося завантажити провайдер HMAC");
        ctx_.reset(EVP_MAC_CTX_new(mac_.get()));
        if (!ctx_) throw std::runtime_error("Не вдалося створити контекст EVP_MAC_CTX");

        std::array<OSSL_PARAM, 2> params{};
        params[0] = OSSL_PARAM_construct_utf8_string(
            OSSL_MAC_PARAM_DIGEST, const_cast<char*>(hash_name.data()), hash_name.size());
        params[1] = OSSL_PARAM_construct_end();

        if (EVP_MAC_init(ctx_.get(), key.data(), key.size(), params.data()) <= 0) {
            throw std::runtime_error("Помилка ініціалізації EVP_MAC_init");
        }
    }

    void update(std::span<const uint8_t> data) {
        if (EVP_MAC_update(ctx_.get(), data.data(), data.size()) <= 0) {
            throw std::runtime_error("Помилка оновлення EVP_MAC_update");
        }
    }

    [[nodiscard]] std::array<uint8_t, 32> finalize() {
        std::array<uint8_t, 32> out{};
        size_t written = 0;
        if (EVP_MAC_final(ctx_.get(), out.data(), &written, out.size()) <= 0) {
            throw std::runtime_error("Помилка фіналізації EVP_MAC_final");
        }
        return out;
    }

private:
    std::unique_ptr<EVP_MAC, decltype(&EVP_MAC_free)> mac_;
    std::unique_ptr<EVP_MAC_CTX, decltype(&EVP_MAC_CTX_free)> ctx_;
};

} // namespace crypto
