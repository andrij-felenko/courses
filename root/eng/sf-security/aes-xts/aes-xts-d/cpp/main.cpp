#include <array>
#include <vector>
#include <span>
#include <cstdint>
#include <cstring>
#include <memory>
#include <expected>

namespace security {

constexpr std::size_t kBlockBytes = 16;
using Block128 = std::array<uint8_t, kBlockBytes>;

enum class CryptError {
    kInvalidKey,
    kBufferTooSmall,
    kEqualKeysRejected
};

class BlockCipher {
public:
    virtual ~BlockCipher() = default;
    virtual void Encrypt(const Block128& in, Block128& out) const noexcept = 0;
    virtual void Decrypt(const Block128& in, Block128& out) const noexcept = 0;
};

class XtsProcessor {
public:
    explicit XtsProcessor(std::unique_ptr<BlockCipher> data_cipher,
                          std::unique_ptr<BlockCipher> tweak_cipher) noexcept
        : data_cipher_(std::move(data_cipher)),
          tweak_cipher_(std::move(tweak_cipher)) {}

    static void GaloisMultiplyAlpha(Block128& t) noexcept {
        uint8_t carry = 0;
        for (std::size_t i = 0; i < kBlockBytes; ++i) {
            uint8_t next_carry = t[i] >> 7;
            t[i] = static_cast<uint8_t>((t[i] << 1) | carry);
            carry = next_carry;
        }
        const uint8_t mask = static_cast<uint8_t>(-(static_cast<int8_t>(carry))) & 0x87;
        t[0] ^= mask;
    }

    [[nodiscard]] std::expected<void, CryptError> EncryptSector(
        const Block128& lba_tweak,
        std::span<const uint8_t> plaintext,
        std::span<uint8_t> ciphertext) const noexcept {

        if (plaintext.size() < kBlockBytes || ciphertext.size() < plaintext.size()) {
            return std::unexpected(CryptError::kBufferTooSmall);
        }

        Block128 t{};
        tweak_cipher_->Encrypt(lba_tweak, t);

        const std::size_t len = plaintext.size();
        const std::size_t full_blocks = len / kBlockBytes;
        const std::size_t rem = len % kBlockBytes;
        const std::size_t lim = (rem == 0) ? full_blocks : (full_blocks - 1);

        Block128 pp{}, cc{};

        for (std::size_t i = 0; i < lim; ++i) {
            const auto offset = i * kBlockBytes;
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                pp[k] = plaintext[offset + k] ^ t[k];
            }
            data_cipher_->Encrypt(pp, cc);
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                ciphertext[offset + k] = cc[k] ^ t[k];
            }
            GaloisMultiplyAlpha(t);
        }

        if (rem > 0) {
            const std::size_t m = full_blocks;
            const auto p_m_minus_1_idx = (m - 1) * kBlockBytes;
            const auto p_m_idx = m * kBlockBytes;

            Block128 c_prime{};
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                pp[k] = plaintext[p_m_minus_1_idx + k] ^ t[k];
            }
            data_cipher_->Encrypt(pp, cc);
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                c_prime[k] = cc[k] ^ t[k];
            }

            std::memcpy(&ciphertext[p_m_idx], c_prime.data(), rem);

            Block128 p_prime{};
            std::memcpy(p_prime.data(), &plaintext[p_m_idx], rem);
            std::memcpy(p_prime.data() + rem, c_prime.data() + rem, kBlockBytes - rem);

            GaloisMultiplyAlpha(t);

            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                pp[k] = p_prime[k] ^ t[k];
            }
            data_cipher_->Encrypt(pp, cc);
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                ciphertext[p_m_minus_1_idx + k] = cc[k] ^ t[k];
            }
        }

        return {};
    }

    [[nodiscard]] std::expected<void, CryptError> DecryptSector(
        const Block128& lba_tweak,
        std::span<const uint8_t> ciphertext,
        std::span<uint8_t> plaintext) const noexcept {

        if (ciphertext.size() < kBlockBytes || plaintext.size() < ciphertext.size()) {
            return std::unexpected(CryptError::kBufferTooSmall);
        }

        Block128 t{};
        tweak_cipher_->Encrypt(lba_tweak, t);

        const std::size_t len = ciphertext.size();
        const std::size_t full_blocks = len / kBlockBytes;
        const std::size_t rem = len % kBlockBytes;
        const std::size_t lim = (rem == 0) ? full_blocks : (full_blocks - 1);

        Block128 cc{}, pp{};

        for (std::size_t i = 0; i < lim; ++i) {
            const auto offset = i * kBlockBytes;
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                cc[k] = ciphertext[offset + k] ^ t[k];
            }
            data_cipher_->Decrypt(cc, pp);
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                plaintext[offset + k] = pp[k] ^ t[k];
            }
            GaloisMultiplyAlpha(t);
        }

        if (rem > 0) {
            const std::size_t m = full_blocks;
            const auto c_m_minus_1_idx = (m - 1) * kBlockBytes;
            const auto c_m_idx = m * kBlockBytes;

            Block128 t_m_minus_1 = t;
            GaloisMultiplyAlpha(t);

            Block128 p_prime{};
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                cc[k] = ciphertext[c_m_minus_1_idx + k] ^ t[k];
            }
            data_cipher_->Decrypt(cc, pp);
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                p_prime[k] = pp[k] ^ t[k];
            }

            std::memcpy(&plaintext[c_m_idx], p_prime.data(), rem);

            Block128 c_prime{};
            std::memcpy(c_prime.data(), &ciphertext[c_m_idx], rem);
            std::memcpy(c_prime.data() + rem, p_prime.data() + rem, kBlockBytes - rem);

            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                cc[k] = c_prime[k] ^ t_m_minus_1[k];
            }
            data_cipher_->Decrypt(cc, pp);
            for (std::size_t k = 0; k < kBlockBytes; ++k) {
                plaintext[c_m_minus_1_idx + k] = pp[k] ^ t_m_minus_1[k];
            }
        }

        return {};
    }

private:
    std::unique_ptr<BlockCipher> data_cipher_;
    std::unique_ptr<BlockCipher> tweak_cipher_;
};

} // namespace security
