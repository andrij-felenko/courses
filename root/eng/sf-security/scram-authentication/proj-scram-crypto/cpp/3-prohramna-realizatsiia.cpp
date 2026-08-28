#include <iostream>
#include <string_view>
#include <span>
#include <array>
#include <vector>
#include <stdexcept>
#include <memory>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

namespace scram {

constexpr size_t hash_size = 32;
using byte_block = std::array<uint8_t, hash_size>;

/* RAII-керування контекстом обчислення дайджестів OpenSSL */
struct md_ctx_destroyer {
    void operator()(EVP_MD_CTX* ctx) const noexcept {
        if (ctx) EVP_MD_CTX_free(ctx);
    }
};
using scoped_md_ctx = std::unique_ptr<EVP_MD_CTX, md_ctx_destroyer>;

/* Обчислення SHA-256 */
[[nodiscard]] byte_block sha256(std::span<const uint8_t> data) {
    scoped_md_ctx ctx(EVP_MD_CTX_new());
    if (!ctx) throw std::runtime_error("Не вдалося виділити EVP_MD_CTX");

    byte_block out{};
    if (!EVP_DigestInit_ex(ctx.get(), EVP_sha256(), nullptr) ||
        !EVP_DigestUpdate(ctx.get(), data.data(), data.size()) ||
        !EVP_DigestFinal_ex(ctx.get(), out.data(), nullptr)) {
        throw std::runtime_error("Помилка обчислення SHA-256");
    }
    return out;
}

/* Обчислення HMAC-SHA-256 */
[[nodiscard]] byte_block hmac_sha256(std::span<const uint8_t> key,
                                     std::span<const uint8_t> message) {
    byte_block out{};
    unsigned int len = hash_size;
    uint8_t* res = HMAC(EVP_sha256(),
                        key.data(), static_cast<int>(key.size()),
                        message.data(), message.size(),
                        out.data(), &len);
    if (!res || len != hash_size) {
        throw std::runtime_error("Помилка обчислення HMAC-SHA-256");
    }
    return out;
}

/* Побітовий виключальний АБО (XOR) двох криптографічних блоків */
[[nodiscard]] byte_block xor_blocks(const byte_block& a, const byte_block& b) noexcept {
    byte_block out{};
    for (size_t i = 0; i < hash_size; ++i) {
        out[i] = a[i] ^ b[i];
    }
    return out;
}

/* Сховище тріади ключів користувача */
struct credential_bundle {
    byte_block client_key;
    byte_block stored_key;
    byte_block server_key;
};

/* Криптографічний рушій SCRAM-SHA-256 */
class scram_service {
public:
    /* Крок 1: Розтягування пароля та соління за алгоритмом PBKDF2 */
    [[nodiscard]] static byte_block derive_salted_password(
        std::string_view password,
        std::span<const uint8_t> salt,
        int iterations) {
        byte_block salted{};
        if (!PKCS5_PBKDF2_HMAC(password.data(), static_cast<int>(password.size()),
                               salt.data(), static_cast<int>(salt.size()),
                               iterations,
                               EVP_sha256(),
                               hash_size, salted.data())) {
            throw std::runtime_error("Збій виконання алгоритму PBKDF2");
        }
        return salted;
    }

    /* Крок 2: Виведення ключів клієнта, сервера та бази даних */
    [[nodiscard]] static credential_bundle derive_credentials(const byte_block& salted_pass) {
        constexpr std::string_view client_tag = "Client Key";
        constexpr std::string_view server_tag = "Server Key";

        auto as_bytes = [](std::string_view sv) {
            return std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(sv.data()), sv.size());
        };

        byte_block ck = hmac_sha256(salted_pass, as_bytes(client_tag));
        byte_block stk = sha256(ck);
        byte_block sk = hmac_sha256(salted_pass, as_bytes(server_tag));

        return { ck, stk, sk };
    }

    /* Крок 3: Формування клієнтського доказу ClientProof */
    [[nodiscard]] static byte_block compute_client_proof(
        const byte_block& client_key,
        const byte_block& stored_key,
        std::string_view auth_message) {
        auto msg_span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(auth_message.data()), auth_message.size());

        byte_block client_signature = hmac_sha256(stored_key, msg_span);
        byte_block proof = xor_blocks(client_key, client_signature);

        OPENSSL_cleanse(client_signature.data(), client_signature.size());
        return proof;
    }

    /* Крок 4: Серверна перевірка доказу та генерація підтвердження */
    [[nodiscard]] static bool server_authenticate(
        const byte_block& stored_key,
        const byte_block& server_key,
        const byte_block& client_proof,
        std::string_view auth_message,
        byte_block& out_server_signature) {

        auto msg_span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(auth_message.data()), auth_message.size());

        /* 1. Обчислення підпису клієнта на стороні сервера */
        byte_block client_sig = hmac_sha256(stored_key, msg_span);

        /* 2. Відновлення ClientKey' = ClientProof XOR ClientSignature */
        byte_block recovered_ck = xor_blocks(client_proof, client_sig);

        /* 3. Отримання StoredKey' = SHA-256(ClientKey') */
        byte_block computed_stk = sha256(recovered_ck);

        /* 4. Верифікація в постійному часі */
        bool valid = (CRYPTO_memcmp(computed_stk.data(), stored_key.data(), hash_size) == 0);

        OPENSSL_cleanse(recovered_ck.data(), recovered_ck.size());
        OPENSSL_cleanse(computed_stk.data(), computed_stk.size());
        OPENSSL_cleanse(client_sig.data(), client_sig.size());

        if (!valid) {
            return false;
        }

        /* 5. Генерація ServerSignature */
        out_server_signature = hmac_sha256(server_key, msg_span);
        return true;
    }

    /* Крок 5: Клієнтська верифікація підпису сервера */
    [[nodiscard]] static bool client_verify_server(
        const byte_block& server_key,
        std::string_view auth_message,
        const byte_block& received_server_signature) {

        auto msg_span = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(auth_message.data()), auth_message.size());

        byte_block expected_sig = hmac_sha256(server_key, msg_span);
        bool match = (CRYPTO_memcmp(expected_sig.data(), received_server_signature.data(), hash_size) == 0);

        OPENSSL_cleanse(expected_sig.data(), expected_sig.size());
        return match;
    }
};

} // namespace scram
