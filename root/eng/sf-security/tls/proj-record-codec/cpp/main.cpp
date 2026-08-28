#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <memory>
#include <stdexcept>
#include <cstring>
#include <openssl/evp.h>

class TlsRecordCodec {
public:
    static constexpr size_t HeaderLen = 5;
    static constexpr size_t TagLen = 16;
    static constexpr size_t MaxPlaintextLen = 16384;

    enum class ContentType : uint8_t {
        ChangeCipherSpec = 20,
        Alert = 21,
        Handshake = 22,
        ApplicationData = 23
    };

    struct DecryptedRecord {
        ContentType type;
        std::vector<uint8_t> data;
    };

    TlsRecordCodec(std::span<const uint8_t, 16> key, std::span<const uint8_t, 12> iv)
        : ctx_(EVP_CIPHER_CTX_new(), &EVP_CIPHER_CTX_free), seq_num_(0) {
        if (!ctx_) {
            throw std::runtime_error("Не вдалося створити контекст OpenSSL EVP");
        }
        std::ranges::copy(key, key_.begin());
        std::ranges::copy(iv, iv_.begin());
    }

    std::vector<uint8_t> protect(ContentType type,
                                 std::span<const uint8_t> plaintext,
                                 size_t padding_len = 0) {
        if (plaintext.size() + 1 + padding_len > MaxPlaintextLen + 256) {
            throw std::length_error("Перевищено максимальний розмір запису TLS");
        }

        auto nonce = make_nonce(seq_num_);

        // 1. Формування відкритого тіла
        std::vector<uint8_t> inner;
        inner.reserve(plaintext.size() + 1 + padding_len);
        inner.insert(inner.end(), plaintext.begin(), plaintext.end());
        inner.push_back(static_cast<uint8_t>(type));
        inner.insert(inner.end(), padding_len, 0x00);

        // 2. Формування зовнішнього заголовка
        const size_t ciphertext_len = inner.size() + TagLen;
        std::vector<uint8_t> out(HeaderLen + ciphertext_len);
        out[0] = 0x17; // opaque_type: application_data
        out[1] = 0x03; // legacy_record_version: TLS 1.2
        out[2] = 0x03;
        out[3] = static_cast<uint8_t>((ciphertext_len >> 8) & 0xFF);
        out[4] = static_cast<uint8_t>(ciphertext_len & 0xFF);

        // 3. Шифрування AES-128-GCM
        int len = 0;
        init_cipher(true, nonce);

        // AAD = перші 5 байтів заголовка
        if (EVP_EncryptUpdate(ctx_.get(), nullptr, &len, out.data(), HeaderLen) != 1 ||
            EVP_EncryptUpdate(ctx_.get(), out.data() + HeaderLen, &len, inner.data(), static_cast<int>(inner.size())) != 1 ||
            EVP_EncryptFinal_ex(ctx_.get(), out.data() + HeaderLen + len, &len) != 1) {
            throw std::runtime_error("Збій при обчисленні шифротексту AEAD");
        }

        // Отримання тегу автентичності
        if (EVP_CIPHER_CTX_ctrl(ctx_.get(), EVP_CTRL_GCM_GET_TAG, TagLen, out.data() + HeaderLen + inner.size()) != 1) {
            throw std::runtime_error("Не вдалося сформувати тег автентичності AEAD");
        }

        ++seq_num_;
        return out;
    }

    DecryptedRecord unprotect(std::span<const uint8_t> record) {
        if (record.size() < HeaderLen + TagLen + 1) {
            throw std::invalid_argument("Кадр занадто малий для запису TLS");
        }

        if (record[0] != 0x17 || record[1] != 0x03 || record[2] != 0x03) {
            throw std::runtime_error("Невірний заголовок сумісності кадру TLS");
        }

        const uint16_t wire_len = (static_cast<uint16_t>(record[3]) << 8) | record[4];
        if (wire_len != record.size() - HeaderLen) {
            throw std::length_error("Невідповідність поля довжини реальному розміру кадру");
        }

        const size_t encrypted_payload_len = wire_len - TagLen;
        const auto tag_span = record.subspan(HeaderLen + encrypted_payload_len, TagLen);
        auto nonce = make_nonce(seq_num_);

        init_cipher(false, nonce);

        std::vector<uint8_t> decrypted(encrypted_payload_len);
        int len = 0;

        // Подача AAD і дешифрування
        if (EVP_DecryptUpdate(ctx_.get(), nullptr, &len, record.data(), HeaderLen) != 1 ||
            EVP_DecryptUpdate(ctx_.get(), decrypted.data(), &len, record.data() + HeaderLen, static_cast<int>(encrypted_payload_len)) != 1) {
            throw std::runtime_error("Помилка обробки AEAD корисного вантажу");
        }

        if (EVP_CIPHER_CTX_ctrl(ctx_.get(), EVP_CTRL_GCM_SET_TAG, TagLen, const_cast<uint8_t*>(tag_span.data())) != 1 ||
            EVP_DecryptFinal_ex(ctx_.get(), decrypted.data() + len, &len) != 1) {
            throw std::runtime_error("Помилка автентифікації запису: bad_record_mac (тег не зійшовся)");
        }

        // Пошук InnerContentType та видалення нулів набивки
        size_t idx = encrypted_payload_len;
        while (idx > 0 && decrypted[idx - 1] == 0x00) {
            --idx;
        }

        if (idx == 0) {
            throw std::runtime_error("Запис містить лише нулі без типу вмісту");
        }

        const auto type = static_cast<ContentType>(decrypted[idx - 1]);
        decrypted.resize(idx - 1);

        ++seq_num_;
        return { type, std::move(decrypted) };
    }

private:
    std::array<uint8_t, 16> key_;
    std::array<uint8_t, 12> iv_;
    std::unique_ptr<EVP_CIPHER_CTX, decltype(&EVP_CIPHER_CTX_free)> ctx_;
    uint64_t seq_num_;

    std::array<uint8_t, 12> make_nonce(uint64_t seq) const {
        std::array<uint8_t, 12> nonce = iv_;
        for (size_t i = 0; i < 8; ++i) {
            nonce[12 - 1 - i] ^= static_cast<uint8_t>((seq >> (i * 8)) & 0xFF);
        }
        return nonce;
    }

    void init_cipher(bool encrypt, const std::array<uint8_t, 12>& nonce) {
        auto cipher_fn = encrypt ? EVP_EncryptInit_ex : EVP_DecryptInit_ex;
        if (cipher_fn(ctx_.get(), EVP_aes_128_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx_.get(), EVP_CTRL_GCM_SET_IVLEN, 12, nullptr) != 1 ||
            cipher_fn(ctx_.get(), nullptr, nullptr, key_.data(), nonce.data()) != 1) {
            throw std::runtime_error("Помилка ініціалізації контексту шифру AES-GCM");
        }
    }
};
