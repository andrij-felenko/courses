#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/sha.h>

inline constexpr uint32_t TPM_GENERATED_VALUE = 0xff544347;
inline constexpr uint16_t TPM_ST_ATTEST_QUOTE = 0x8018;
inline constexpr size_t SHA256_LEN = 32;

using Sha256Digest = std::array<uint8_t, SHA256_LEN>;

struct BootEvent {
    uint32_t pcr_index;
    Sha256Digest digest;
    std::string event_name;
};

/* RAII-обгортка для автоматичного керування життєвим циклом контексту OpenSSL */
struct EvpMdCtxDeleter {
    void operator()(EVP_MD_CTX* ctx) const noexcept {
        if (ctx) EVP_MD_CTX_free(ctx);
    }
};
using UniqueEvpMdCtx = std::unique_ptr<EVP_MD_CTX, EvpMdCtxDeleter>;

class Tpm2QuoteVerifier {
public:
    static Sha256Digest extend_pcr(const Sha256Digest& current_pcr, const Sha256Digest& event_digest) noexcept {
        std::array<uint8_t, SHA256_LEN * 2> buffer{};
        std::memcpy(buffer.data(), current_pcr.data(), SHA256_LEN);
        std::memcpy(buffer.data() + SHA256_LEN, event_digest.data(), SHA256_LEN);

        Sha256Digest next_pcr{};
        SHA256(buffer.data(), buffer.size(), next_pcr.data());
        return next_pcr;
    }

    static bool verify_signature(
        EVP_PKEY* ak_pubkey,
        std::span<const uint8_t> data,
        std::span<const uint8_t> signature) noexcept
    {
        if (!ak_pubkey) return false;

        UniqueEvpMdCtx ctx(EVP_MD_CTX_new());
        if (!ctx) return false;

        if (EVP_DigestVerifyInit(ctx.get(), nullptr, EVP_sha256(), nullptr, ak_pubkey) != 1) {
            return false;
        }
        if (EVP_DigestVerifyUpdate(ctx.get(), data.data(), data.size()) != 1) {
            return false;
        }
        return EVP_DigestVerifyFinal(ctx.get(), signature.data(), signature.size()) == 1;
    }

    static std::expected<bool, std::string> verify_attestation(
        std::span<const uint8_t> raw_attest_buf,
        uint32_t magic,
        uint16_t type,
        std::span<const uint8_t> extra_data,
        const Sha256Digest& quoted_pcr_digest,
        std::span<const uint8_t> signature,
        EVP_PKEY* ak_pubkey,
        std::span<const uint8_t> expected_nonce,
        std::span<const BootEvent> event_log)
    {
        if (magic != TPM_GENERATED_VALUE) {
            return std::unexpected("Недійсне магічне число TPM");
        }
        if (type != TPM_ST_ATTEST_QUOTE) {
            return std::unexpected("Тип структури не є TPM_ST_ATTEST_QUOTE");
        }
        if (extra_data.size() != expected_nonce.size() ||
            !std::equal(extra_data.begin(), extra_data.end(), expected_nonce.begin())) {
            return std::unexpected("Невідповідність Nonce: можлива атака повторного відтворення");
        }

        if (!verify_signature(ak_pubkey, raw_attest_buf, signature)) {
            return std::unexpected("Криптографічний підпис AK недійсний");
        }

        /* Відтворення стану регістра PCR[0] */
        Sha256Digest simulated_pcr0{};
        for (const auto& ev : event_log) {
            if (ev.pcr_index == 0) {
                simulated_pcr0 = extend_pcr(simulated_pcr0, ev.digest);
            }
        }

        if (simulated_pcr0 != quoted_pcr_digest) {
            return std::unexpected("Розбіжність PCR: журнал завантаження не відповідає підписаному стану чипа");
        }

        return true;
    }
};
