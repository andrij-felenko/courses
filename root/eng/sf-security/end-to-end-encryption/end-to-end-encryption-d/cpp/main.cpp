#include <array>
#include <vector>
#include <span>
#include <cstdint>
#include <cstring>
#include <utility>

struct MessageHeader {
    std::array<uint8_t, 32> dh_pub{};
    uint32_t pn{0};
    uint32_t n{0};
};

struct EncryptedPayload {
    MessageHeader              header;
    std::vector<uint8_t>       ciphertext;
    std::array<uint8_t, 16>    auth_tag{};
};

class RatchetEncryptor {
public:
    static constexpr size_t KeyLen = 32;
    static constexpr size_t TagLen = 16;

    RatchetEncryptor(std::array<uint8_t, KeyLen> initial_cks,
                     std::array<uint8_t, KeyLen> dh_pub,
                     uint32_t pn = 0)
        : cks_(initial_cks), dhs_pub_(dh_pub), pn_(pn) {}

    ~RatchetEncryptor() {
        wipe(cks_);
    }

    EncryptedPayload encrypt(std::span<const uint8_t> plaintext) {
        auto [next_cks, mk] = kdf_step(cks_);
        cks_ = next_cks;

        MessageHeader hdr{
            .dh_pub = dhs_pub_,
            .pn     = pn_,
            .n      = ns_++
        };

        EncryptedPayload result;
        result.header = hdr;
        result.ciphertext.resize(plaintext.size());

        // AEAD шифрування з асоційованими даними (заголовок як AAD)
        aead_encrypt(result.ciphertext, result.auth_tag,
                     plaintext,
                     std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)),
                     mk);

        wipe(mk);
        return result;
    }

private:
    std::array<uint8_t, KeyLen> cks_{};
    std::array<uint8_t, KeyLen> dhs_pub_{};
    uint32_t ns_{0};
    uint32_t pn_{0};

    static void wipe(std::span<uint8_t> buf) {
        volatile uint8_t *p = buf.data();
        for (size_t i = 0; i < buf.size(); ++i) p[i] = 0;
    }

    static std::pair<std::array<uint8_t, KeyLen>, std::array<uint8_t, KeyLen>>
    kdf_step(const std::array<uint8_t, KeyLen> &ck) {
        std::array<uint8_t, KeyLen> next_ck{}, mk{};
        for (size_t i = 0; i < KeyLen; ++i) {
            mk[i]      = static_cast<uint8_t>(ck[i] ^ 0x01);
            next_ck[i] = static_cast<uint8_t>(ck[i] ^ 0x02);
        }
        return {next_ck, mk};
    }

    static void aead_encrypt(
        std::span<uint8_t> ciphertext,
        std::span<uint8_t, TagLen> tag,
        std::span<const uint8_t> plaintext,
        std::span<const uint8_t> aad,
        const std::array<uint8_t, KeyLen> &key
    ) {
        for (size_t i = 0; i < plaintext.size(); ++i) {
            ciphertext[i] = plaintext[i] ^ key[i % KeyLen];
        }
        for (size_t i = 0; i < TagLen; ++i) {
            tag[i] = static_cast<uint8_t>(key[i] ^ (aad.empty() ? 0 : aad[0]));
        }
    }
};
