#include <array>
#include <vector>
#include <span>
#include <cstdint>
#include <cstring>
#include <expected>
#include <algorithm>
#include <memory>

namespace security {

constexpr std::size_t kAesBlockSize = 16;
using Block = std::array<uint8_t, kAesBlockSize>;

enum class XtsError {
    kInvalidKeyLength,
    kDataTooShort,
    kInvalidBufferSizes,
    kIdenticalKeysRejected
};

class AesCipher {
public:
    virtual ~AesCipher() = default;
    virtual void EncryptBlock(const Block& in, Block& out) const noexcept = 0;
    virtual void DecryptBlock(const Block& in, Block& out) const noexcept = 0;
};

class XtsEngine {
public:
    explicit XtsEngine(std::unique_ptr<AesCipher> data_cipher,
                       std::unique_ptr<AesCipher> tweak_cipher) noexcept
        : data_cipher_(std::move(data_cipher)), tweak_cipher_(std::move(tweak_cipher)) {}

    [[nodiscard]] static void MultiplyAlpha(Block& t) noexcept {
        uint8_t carry = 0;
        for (std::size_t i = 0; i < kAesBlockSize; ++i) {
            uint8_t next_carry = t[i] >> 7;
            t[i] = static_cast<uint8_t>((t[i] << 1) | carry);
            carry = next_carry;
        }
        const uint8_t mask = static_cast<uint8_t>(-(static_cast<int8_t>(carry))) & 0x87;
        t[0] ^= mask;
    }

    [[nodiscard]] std::expected<void, XtsError> EncryptSector(
        const Block& tweak_input,
        std::span<const uint8_t> plaintext,
        std::span<uint8_t> ciphertext) const noexcept {

        if (plaintext.size() < kAesBlockSize || ciphertext.size() < plaintext.size()) {
            return std::unexpected(XtsError::kDataTooShort);
        }

        Block t{};
        tweak_cipher_->EncryptBlock(tweak_input, t);

        const std::size_t len = plaintext.size();
        const std::size_t full_blocks = len / kAesBlockSize;
        const std::size_t remainder = len % kAesBlockSize;
        const std::size_t lim = (remainder == 0) ? full_blocks : (full_blocks - 1);

        Block pp{}, cc{};

        for (std::size_t i = 0; i < lim; ++i) {
            const auto p_offset = i * kAesBlockSize;
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                pp[k] = plaintext[p_offset + k] ^ t[k];
            }
            data_cipher_->EncryptBlock(pp, cc);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                ciphertext[p_offset + k] = cc[k] ^ t[k];
            }
            MultiplyAlpha(t);
        }

        if (remainder > 0) {
            const std::size_t m = full_blocks;
            const auto p_m_minus_1_offset = (m - 1) * kAesBlockSize;
            const auto p_m_offset = m * kAesBlockSize;

            Block c_prime{};
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                pp[k] = plaintext[p_m_minus_1_offset + k] ^ t[k];
            }
            data_cipher_->EncryptBlock(pp, cc);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                c_prime[k] = cc[k] ^ t[k];
            }

            // Викрадення шифротексту: збереження перших remainder байтів
            std::memcpy(&ciphertext[p_m_offset], c_prime.data(), remainder);

            Block p_prime{};
            std::memcpy(p_prime.data(), &plaintext[p_m_offset], remainder);
            std::memcpy(p_prime.data() + remainder, c_prime.data() + remainder, kAesBlockSize - remainder);

            MultiplyAlpha(t);

            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                pp[k] = p_prime[k] ^ t[k];
            }
            data_cipher_->EncryptBlock(pp, cc);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                ciphertext[p_m_minus_1_offset + k] = cc[k] ^ t[k];
            }
        }

        return {};
    }

    [[nodiscard]] std::expected<void, XtsError> DecryptSector(
        const Block& tweak_input,
        std::span<const uint8_t> ciphertext,
        std::span<uint8_t> plaintext) const noexcept {

        if (ciphertext.size() < kAesBlockSize || plaintext.size() < ciphertext.size()) {
            return std::unexpected(XtsError::kDataTooShort);
        }

        Block t{};
        tweak_cipher_->EncryptBlock(tweak_input, t);

        const std::size_t len = ciphertext.size();
        const std::size_t full_blocks = len / kAesBlockSize;
        const std::size_t remainder = len % kAesBlockSize;
        const std::size_t lim = (remainder == 0) ? full_blocks : (full_blocks - 1);

        Block cc{}, pp{};

        for (std::size_t i = 0; i < lim; ++i) {
            const auto c_offset = i * kAesBlockSize;
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                cc[k] = ciphertext[c_offset + k] ^ t[k];
            }
            data_cipher_->DecryptBlock(cc, pp);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                plaintext[c_offset + k] = pp[k] ^ t[k];
            }
            MultiplyAlpha(t);
        }

        if (remainder > 0) {
            const std::size_t m = full_blocks;
            const auto c_m_minus_1_offset = (m - 1) * kAesBlockSize;
            const auto c_m_offset = m * kAesBlockSize;

            Block t_m_minus_1 = t;
            MultiplyAlpha(t);

            Block p_prime{};
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                cc[k] = ciphertext[c_m_minus_1_offset + k] ^ t[k];
            }
            data_cipher_->DecryptBlock(cc, pp);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                p_prime[k] = pp[k] ^ t[k];
            }

            std::memcpy(&plaintext[c_m_offset], p_prime.data(), remainder);

            Block c_prime{};
            std::memcpy(c_prime.data(), &ciphertext[c_m_offset], remainder);
            std::memcpy(c_prime.data() + remainder, p_prime.data() + remainder, kAesBlockSize - remainder);

            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                cc[k] = c_prime[k] ^ t_m_minus_1[k];
            }
            data_cipher_->DecryptBlock(cc, pp);
            for (std::size_t k = 0; k < kAesBlockSize; ++k) {
                plaintext[c_m_minus_1_offset + k] = pp[k] ^ t_m_minus_1[k];
            }
        }

        return {};
    }

private:
    std::unique_ptr<AesCipher> data_cipher_;
    std::unique_ptr<AesCipher> tweak_cipher_;
};

} // namespace security
