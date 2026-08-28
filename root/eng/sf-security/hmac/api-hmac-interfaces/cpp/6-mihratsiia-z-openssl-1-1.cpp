// Застарілий підхід OpenSSL 1.1.1 з використанням RAII-обгортки (deprecated у 3.0)
#include <memory>
#include <span>
#include <array>
#include <openssl/hmac.h>

namespace legacy {

[[nodiscard]] std::array<uint8_t, 32> hmac_sha256(
    std::span<const uint8_t> key,
    std::span<const uint8_t> data)
{
    std::unique_ptr<HMAC_CTX, decltype(&HMAC_CTX_free)> ctx(HMAC_CTX_new(), HMAC_CTX_free);
    if (!ctx) return {};

    HMAC_Init_ex(ctx.get(), key.data(), static_cast<int>(key.size()), EVP_sha256(), nullptr);
    HMAC_Update(ctx.get(), data.data(), data.size());
    std::array<uint8_t, 32> out{};
    unsigned int len = 0;
    HMAC_Final(ctx.get(), out.data(), &len);
    return out;
}

} // namespace legacy
