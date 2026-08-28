#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <span>
#include <stdexcept>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/ec.h>
#include <openssl/kdf.h>
#include <openssl/core_names.h>
#include <openssl/rand.h>

// RAII обгортки для структур OpenSSL
struct EvpPkeyDeleter { void operator()(EVP_PKEY* p) const { EVP_PKEY_free(p); } };
struct EvpPkeyCtxDeleter { void operator()(EVP_PKEY_CTX* p) const { EVP_PKEY_CTX_free(p); } };
struct EvpCipherCtxDeleter { void operator()(EVP_CIPHER_CTX* p) const { EVP_CIPHER_CTX_free(p); } };
struct EvpKdfCtxDeleter { void operator()(EVP_KDF_CTX* p) const { EVP_KDF_CTX_free(p); } };

using ScopedEVP_PKEY = std::unique_ptr<EVP_PKEY, EvpPkeyDeleter>;
using ScopedEVP_PKEY_CTX = std::unique_ptr<EVP_PKEY_CTX, EvpPkeyCtxDeleter>;
using ScopedEVP_CIPHER_CTX = std::unique_ptr<EVP_CIPHER_CTX, EvpCipherCtxDeleter>;
using ScopedEVP_KDF_CTX = std::unique_ptr<EVP_KDF_CTX, EvpKdfCtxDeleter>;

class WebPushEncryptor {
public:
    // Шифрує відкритий текст для клієнта за стандартом RFC 8291
    static std::vector<uint8_t> encrypt(
        std::span<const uint8_t> client_p256dh,
        std::span<const uint8_t> client_auth,
        std::string_view plaintext,
        uint32_t record_size = 4096)
    {
        if (client_p256dh.size() != 65 || client_p256dh[0] != 0x04) {
            throw std::invalid_argument("Некоректний публічний ключ клієнта (має бути 65 байтів uncompressed)");
        }
        if (client_auth.size() != 16) {
            throw std::invalid_argument("Секрет auth має мати довжину рівно 16 байтів");
        }

        // 1. Генерація ефемерної пари ключів сервера (NIST P-256)
        ScopedEVP_PKEY_CTX gen_ctx(EVP_PKEY_CTX_new_id(EVP_PKEY_EC, nullptr));
        if (!gen_ctx || EVP_PKEY_keygen_init(gen_ctx.get()) <= 0) {
            throw std::runtime_error("Помилка ініціалізації генератора ключів EC");
        }
        if (EVP_PKEY_CTX_set_ec_paramgen_curve_nid(gen_ctx.get(), NID_X9_62_prime256v1) <= 0) {
            throw std::runtime_error("Помилка вибору кривої P-256");
        }
        EVP_PKEY* raw_server_key = nullptr;
        if (EVP_PKEY_keygen(gen_ctx.get(), &raw_server_key) <= 0) {
            throw std::runtime_error("Помилка генерації ефемерного ключа сервера");
        }
        ScopedEVP_PKEY server_key(raw_server_key);

        // Експорт публічного ключа сервера (65 байтів)
        std::vector<uint8_t> server_pub(65);
        size_t server_pub_len = 65;
        if (EVP_PKEY_get_octet_string_param(server_key.get(), OSSL_PKEY_PARAM_PUB_KEY,
                                            server_pub.data(), server_pub.size(), &server_pub_len) <= 0) {
            throw std::runtime_error("Помилка експорту публічного ключа сервера");
        }

        // 2. Імпорт публічного ключа клієнта
        ScopedEVP_PKEY_CTX peer_ctx(EVP_PKEY_CTX_new_id(EVP_PKEY_EC, nullptr));
        EVP_PKEY_paramgen_init(peer_ctx.get());
        EVP_PKEY_CTX_set_ec_paramgen_curve_nid(peer_ctx.get(), NID_X9_62_prime256v1);
        EVP_PKEY* raw_peer_params = nullptr;
        EVP_PKEY_paramgen(peer_ctx.get(), &raw_peer_params);
        ScopedEVP_PKEY peer_params(raw_peer_params);

        EVP_PKEY* raw_peer_key = nullptr;
        ScopedEVP_PKEY_CTX import_ctx(EVP_PKEY_CTX_new_from_pkey(nullptr, peer_params.get(), nullptr));
        if (!import_ctx || EVP_PKEY_fromdata_init(import_ctx.get()) <= 0) {
            throw std::runtime_error("Помилка ініціалізації імпорту ключа клієнта");
        }

        OSSL_PARAM params[] = {
            OSSL_PARAM_construct_utf8_string(OSSL_PKEY_PARAM_GROUP_NAME, const_cast<char*>("prime256v1"), 0),
            OSSL_PARAM_construct_octet_string(OSSL_PKEY_PARAM_PUB_KEY, const_cast<uint8_t*>(client_p256dh.data()), client_p256dh.size()),
            OSSL_PARAM_construct_end()
        };
        if (EVP_PKEY_fromdata(import_ctx.get(), &raw_peer_key, EVP_PKEY_PUBLIC_KEY, params) <= 0) {
            throw std::runtime_error("Помилка імпорту точки відкритого ключа клієнта");
        }
        ScopedEVP_PKEY peer_key(raw_peer_key);

        // 3. Обчислення спільного секрету ECDH
        ScopedEVP_PKEY_CTX derive_ctx(EVP_PKEY_CTX_new(server_key.get(), nullptr));
        if (!derive_ctx || EVP_PKEY_derive_init(derive_ctx.get()) <= 0 ||
            EVP_PKEY_derive_set_peer(derive_ctx.get(), peer_key.get()) <= 0) {
            throw std::runtime_error("Помилка налаштування контексту ECDH");
        }
        size_t ecdh_secret_len = 0;
        EVP_PKEY_derive(derive_ctx.get(), nullptr, &ecdh_secret_len);
        std::vector<uint8_t> ecdh_secret(ecdh_secret_len);
        if (EVP_PKEY_derive(derive_ctx.get(), ecdh_secret.data(), &ecdh_secret_len) <= 0) {
            throw std::runtime_error("Помилка обчислення секрету ECDH");
        }

        // 4. Виведення IKM через HKDF з auth secret
        // key_info = "WebPush: info\0" || client_p256dh || server_pub
        std::vector<uint8_t> key_info;
        const std::string_view info_prefix = "WebPush: info";
        key_info.insert(key_info.end(), info_prefix.begin(), info_prefix.end());
        key_info.push_back(0x00);
        key_info.insert(key_info.end(), client_p256dh.begin(), client_p256dh.end());
        key_info.insert(key_info.end(), server_pub.begin(), server_pub.end());

        std::vector<uint8_t> ikm = hkdf_derive(client_auth, ecdh_secret, key_info, 32);

        // 5. Генерація випадкової солі (16 байтів)
        std::vector<uint8_t> salt(16);
        if (RAND_bytes(salt.data(), static_cast<int>(salt.size())) <= 0) {
            throw std::runtime_error("Помилка CSPRNG при генерації солі");
        }

        // 6. Виведення CEK (16 байтів) та Nonce (12 байтів)
        const std::string_view cek_info = "Content-Encoding: aes128gcm";
        std::vector<uint8_t> cek_info_bytes(cek_info.begin(), cek_info.end());
        cek_info_bytes.push_back(0x00);
        std::vector<uint8_t> cek = hkdf_derive(salt, ikm, cek_info_bytes, 16);

        const std::string_view nonce_info = "Content-Encoding: nonce";
        std::vector<uint8_t> nonce_info_bytes(nonce_info.begin(), nonce_info.end());
        nonce_info_bytes.push_back(0x00);
        std::vector<uint8_t> nonce = hkdf_derive(salt, ikm, nonce_info_bytes, 12);

        // 7. Формування доповнення відкритого тексту (Padding)
        // Додаємо байт 0x02 як розділювач останнього блоку
        std::vector<uint8_t> padded(plaintext.begin(), plaintext.end());
        padded.push_back(0x02);

        // 8. Шифрування AES-128-GCM
        ScopedEVP_CIPHER_CTX cipher_ctx(EVP_CIPHER_CTX_new());
        if (!cipher_ctx || EVP_EncryptInit_ex(cipher_ctx.get(), EVP_aes_128_gcm(), nullptr, nullptr, nullptr) <= 0) {
            throw std::runtime_error("Помилка ініціалізації шифру AES-128-GCM");
        }
        if (EVP_CIPHER_CTX_ctrl(cipher_ctx.get(), EVP_CTRL_GCM_SET_IVLEN, static_cast<int>(nonce.size()), nullptr) <= 0) {
            throw std::runtime_error("Помилка встановлення довжини Nonce");
        }
        if (EVP_EncryptInit_ex(cipher_ctx.get(), nullptr, nullptr, cek.data(), nonce.data()) <= 0) {
            throw std::runtime_error("Помилка передачі ключа та IV в AES-GCM");
        }

        std::vector<uint8_t> ciphertext(padded.size());
        int out_len = 0;
        if (EVP_EncryptUpdate(cipher_ctx.get(), ciphertext.data(), &out_len, padded.data(), static_cast<int>(padded.size())) <= 0) {
            throw std::runtime_error("Помилка шифрування блоку даних");
        }
        int final_len = 0;
        if (EVP_EncryptFinal_ex(cipher_ctx.get(), ciphertext.data() + out_len, &final_len) <= 0) {
            throw std::runtime_error("Помилка фіналізації шифру");
        }

        std::vector<uint8_t> tag(16);
        if (EVP_CIPHER_CTX_ctrl(cipher_ctx.get(), EVP_CTRL_GCM_GET_TAG, static_cast<int>(tag.size()), tag.data()) <= 0) {
            throw std::runtime_error("Помилка отримання тегу автентичності GCM");
        }

        // 9. Складання фінального бінарного кадру aes128gcm
        // [salt (16 B)] || [rs (4 B)] || [idlen = 65 (1 B)] || [server_pub (65 B)] || [ciphertext] || [tag (16 B)]
        std::vector<uint8_t> payload;
        payload.reserve(16 + 4 + 1 + 65 + ciphertext.size() + tag.size());

        payload.insert(payload.end(), salt.begin(), salt.end());

        // Запис record_size як 32-бітного числа Big-Endian
        payload.push_back(static_cast<uint8_t>((record_size >> 24) & 0xFF));
        payload.push_back(static_cast<uint8_t>((record_size >> 16) & 0xFF));
        payload.push_back(static_cast<uint8_t>((record_size >> 8) & 0xFF));
        payload.push_back(static_cast<uint8_t>(record_size & 0xFF));

        payload.push_back(static_cast<uint8_t>(server_pub.size())); // idlen = 65
        payload.insert(payload.end(), server_pub.begin(), server_pub.end());
        payload.insert(payload.end(), ciphertext.begin(), ciphertext.end());
        payload.insert(payload.end(), tag.begin(), tag.end());

        return payload;
    }

private:
    static std::vector<uint8_t> hkdf_derive(
        std::span<const uint8_t> salt,
        std::span<const uint8_t> ikm,
        std::span<const uint8_t> info,
        size_t out_len)
    {
        EVP_KDF* kdf = EVP_KDF_fetch(nullptr, "HKDF", nullptr);
        if (!kdf) throw std::runtime_error("HKDF алгоритм недоступний в OpenSSL");
        ScopedEVP_KDF_CTX kdf_ctx(EVP_KDF_CTX_new(kdf));
        EVP_KDF_free(kdf);

        OSSL_PARAM params[5];
        params[0] = OSSL_PARAM_construct_utf8_string(OSSL_KDF_PARAM_DIGEST, const_cast<char*>("SHA256"), 0);
        params[1] = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_SALT, const_cast<uint8_t*>(salt.data()), salt.size());
        params[2] = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_KEY, const_cast<uint8_t*>(ikm.data()), ikm.size());
        params[3] = OSSL_PARAM_construct_octet_string(OSSL_KDF_PARAM_INFO, const_cast<uint8_t*>(info.data()), info.size());
        params[4] = OSSL_PARAM_construct_end();

        std::vector<uint8_t> out(out_len);
        if (EVP_KDF_derive(kdf_ctx.get(), out.data(), out.size(), params) <= 0) {
            throw std::runtime_error("Помилка виконання HKDF");
        }
        return out;
    }
};
