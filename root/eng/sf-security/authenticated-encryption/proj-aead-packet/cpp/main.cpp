#include <cstdint>
#include <vector>
#include <span>
#include <array>
#include <expected>
#include <memory>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/crypto.h>

#if defined(_WIN32)
#include <winsock2.h>
#else
#include <arpa/inet.h>
#endif

enum class AeadError {
    InvalidInput,
    ContextAllocationFailed,
    CryptoOperationFailed,
    PacketTooShort,
    InvalidHeader,
    ReplayDetected,
    AuthenticationFailed
};

#pragma pack(push, 1)
struct PacketHeader {
    uint16_t magic{0x5345};
    uint16_t version{0x0100};
    uint16_t msg_type{0};
    uint16_t reserved{0};
    uint64_t seq_num{0};
};
#pragma pack(pop)

class AeadChannel {
public:
    static constexpr size_t KeySize = 32;   // AES-256
    static constexpr size_t IvSize  = 12;   // 96-біт Nonce
    static constexpr size_t TagSize = 16;   // 128-біт Tag
    static constexpr size_t WindowSize = 64; // Ковзне вікно

    AeadChannel(std::span<const uint8_t, KeySize> key, std::span<const uint8_t, IvSize> iv_base)
        : tx_seq_(0), rx_max_seq_(0), replay_bitmap_(0) {
        std::memcpy(key_.data(), key.data(), KeySize);
        std::memcpy(iv_base_.data(), iv_base.data(), IvSize);
    }

    ~AeadChannel() {
        OPENSSL_cleanse(key_.data(), key_.size());
        OPENSSL_cleanse(iv_base_.data(), iv_base_.size());
    }

    // Заборона копіювання для запобігання дублюванню лічильників Nonce
    AeadChannel(const AeadChannel&) = delete;
    AeadChannel& operator=(const AeadChannel&) = delete;
    AeadChannel(AeadChannel&&) noexcept = default;
    AeadChannel& operator=(AeadChannel&&) noexcept = default;

    std::expected<std::vector<uint8_t>, AeadError> encrypt(
        uint16_t msg_type,
        std::span<const uint8_t> plaintext
    ) {
        PacketHeader hdr{
            .magic = htons(0x5345),
            .version = htons(0x0100),
            .msg_type = htons(msg_type),
            .reserved = 0,
            .seq_num = htobe64(tx_seq_)
        };

        auto nonce = derive_nonce(tx_seq_);
        tx_seq_++; // Суворо монотонний крок

        auto ctx = make_evp_ctx();
        if (!ctx) return std::unexpected(AeadError::ContextAllocationFailed);

        if (EVP_EncryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_AEAD_SET_IVLEN, IvSize, nullptr) != 1 ||
            EVP_EncryptInit_ex(ctx.get(), nullptr, nullptr, key_.data(), nonce.data()) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        int len = 0;
        // Подання AAD (Заголовок)
        if (EVP_EncryptUpdate(ctx.get(), nullptr, &len, reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        std::vector<uint8_t> frame(sizeof(PacketHeader) + plaintext.size() + TagSize);
        std::memcpy(frame.data(), &hdr, sizeof(hdr));

        uint8_t* ciphertext_ptr = frame.data() + sizeof(PacketHeader);
        if (EVP_EncryptUpdate(ctx.get(), ciphertext_ptr, &len, plaintext.data(), static_cast<int>(plaintext.size())) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        if (EVP_EncryptFinal_ex(ctx.get(), ciphertext_ptr + len, &len) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        uint8_t* tag_ptr = ciphertext_ptr + plaintext.size();
        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_AEAD_GET_TAG, TagSize, tag_ptr) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        OPENSSL_cleanse(nonce.data(), nonce.size());
        return frame;
    }

    struct DecryptedMessage {
        uint16_t msg_type;
        std::vector<uint8_t> payload;
    };

    std::expected<DecryptedMessage, AeadError> decrypt(std::span<const uint8_t> frame) {
        if (frame.size() < sizeof(PacketHeader) + TagSize) {
            return std::unexpected(AeadError::PacketTooShort);
        }

        PacketHeader hdr;
        std::memcpy(&hdr, frame.data(), sizeof(hdr));

        if (ntohs(hdr.magic) != 0x5345 || ntohs(hdr.version) != 0x0100) {
            return std::unexpected(AeadError::InvalidHeader);
        }

        uint64_t seq = be64toh(hdr.seq_num);
        if (!check_replay(seq)) {
            return std::unexpected(AeadError::ReplayDetected);
        }

        size_t ciphertext_len = frame.size() - sizeof(PacketHeader) - TagSize;
        const uint8_t* ciphertext_ptr = frame.data() + sizeof(PacketHeader);
        const uint8_t* tag_ptr = frame.data() + sizeof(PacketHeader) + ciphertext_len;

        auto nonce = derive_nonce(seq);
        auto ctx = make_evp_ctx();
        if (!ctx) return std::unexpected(AeadError::ContextAllocationFailed);

        if (EVP_DecryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_AEAD_SET_IVLEN, IvSize, nullptr) != 1 ||
            EVP_DecryptInit_ex(ctx.get(), nullptr, nullptr, key_.data(), nonce.data()) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        int len = 0;
        // Подання AAD
        if (EVP_DecryptUpdate(ctx.get(), nullptr, &len, reinterpret_cast<const uint8_t*>(&hdr), sizeof(hdr)) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        std::vector<uint8_t> plaintext(ciphertext_len);
        if (EVP_DecryptUpdate(ctx.get(), plaintext.data(), &len, ciphertext_ptr, static_cast<int>(ciphertext_len)) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        if (EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_AEAD_SET_TAG, TagSize, const_cast<uint8_t*>(tag_ptr)) != 1) {
            return std::unexpected(AeadError::CryptoOperationFailed);
        }

        // Бар'єр верифікації
        if (EVP_DecryptFinal_ex(ctx.get(), plaintext.data() + len, &len) <= 0) {
            OPENSSL_cleanse(plaintext.data(), plaintext.size());
            return std::unexpected(AeadError::AuthenticationFailed);
        }

        update_replay(seq);
        OPENSSL_cleanse(nonce.data(), nonce.size());

        return DecryptedMessage{
            .msg_type = ntohs(hdr.msg_type),
            .payload = std::move(plaintext)
        };
    }

private:
    std::array<uint8_t, KeySize> key_{};
    std::array<uint8_t, IvSize>  iv_base_{};
    uint64_t tx_seq_{0};
    uint64_t rx_max_seq_{0};
    uint64_t replay_bitmap_{0};

    struct EvpCtxDeleter {
        void operator()(EVP_CIPHER_CTX* ptr) const noexcept {
            if (ptr) EVP_CIPHER_CTX_free(ptr);
        }
    };
    using EvpCtxPtr = std::unique_ptr<EVP_CIPHER_CTX, EvpCtxDeleter>;

    static EvpCtxPtr make_evp_ctx() {
        return EvpCtxPtr(EVP_CIPHER_CTX_new());
    }

    std::array<uint8_t, IvSize> derive_nonce(uint64_t seq) const noexcept {
        std::array<uint8_t, IvSize> out;
        std::memcpy(out.data(), iv_base_.data(), IvSize);
        for (size_t i = 0; i < 8; ++i) {
            out[IvSize - 1 - i] ^= static_cast<uint8_t>((seq >> (i * 8)) & 0xFF);
        }
        return out;
    }

    bool check_replay(uint64_t seq) const noexcept {
        if (seq == 0 && rx_max_seq_ == 0 && replay_bitmap_ == 0) return true;
        if (seq > rx_max_seq_) return true;
        uint64_t diff = rx_max_seq_ - seq;
        if (diff >= WindowSize) return false;
        if (replay_bitmap_ & (1ULL << diff)) return false;
        return true;
    }

    void update_replay(uint64_t seq) noexcept {
        if (seq > rx_max_seq_) {
            uint64_t diff = seq - rx_max_seq_;
            if (diff < WindowSize) {
                replay_bitmap_ = (replay_bitmap_ << diff) | 1ULL;
            } else {
                replay_bitmap_ = 1ULL;
            }
            rx_max_seq_ = seq;
        } else {
            uint64_t diff = rx_max_seq_ - seq;
            if (diff < WindowSize) {
                replay_bitmap_ |= (1ULL << diff);
            }
        }
    }
};
