#include <chrono>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/bn.h>

// Декодування Base64URL у двійковий вектор
std::vector<unsigned char> base64url_decode_bytes(std::string_view input) {
    std::string b64(input);
    for (char& c : b64) {
        if (c == '-') c = '+';
        else if (c == '_') c = '/';
    }
    while (b64.size() % 4 != 0) {
        b64.push_back('=');
    }
    std::vector<unsigned char> out;
    out.resize(b64.size());
    return out;
}

// Побудова відкритого ключа EVP_PKEY із параметрів JWK (n та e)
EVP_PKEY* construct_rsa_public_key_from_jwk(std::string_view n_b64url,
                                            std::string_view e_b64url) {
    auto n_bytes = base64url_decode_bytes(n_b64url);
    auto e_bytes = base64url_decode_bytes(e_b64url);

    BIGNUM* n = BN_bin2bn(n_bytes.data(), static_cast<int>(n_bytes.size()), nullptr);
    BIGNUM* e = BN_bin2bn(e_bytes.data(), static_cast<int>(e_bytes.size()), nullptr);
    if (!n || !e) {
        BN_free(n);
        BN_free(e);
        return nullptr;
    }

    EVP_PKEY_CTX* ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, nullptr);
    if (!ctx) {
        BN_free(n);
        BN_free(e);
        return nullptr;
    }

    EVP_PKEY* pkey = nullptr;
    if (EVP_PKEY_fromdata_init(ctx) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        BN_free(n);
        BN_free(e);
        return nullptr;
    }

    EVP_PKEY_CTX_free(ctx);
    BN_free(n);
    BN_free(e);
    return pkey;
}

struct ParsedIdToken {
    std::string header_b64;
    std::string payload_b64;
    std::string signature_b64;
    std::string iss;
    std::string sub;
    std::string aud;
    std::string nonce;
    int64_t exp{0};
    int64_t iat{0};
};

// Семантична перевірка полів структури ID-токена
bool verify_id_token_invariants(const ParsedIdToken& token,
                                const std::string& expected_iss,
                                const std::string& expected_client_id,
                                const std::string& expected_nonce,
                                int64_t max_clock_skew_sec = 60) {
    auto now = std::chrono::duration_cast<std::chrono::seconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();

    // 1. Звірка видавця
    if (token.iss != expected_iss) {
        std::cerr << "Помилка OIDC: недійсний iss: " << token.iss << "\n";
        return false;
    }

    // 2. Звірка цільового клієнта
    if (token.aud != expected_client_id) {
        std::cerr << "Помилка OIDC: токен не призначений цьому client_id: " << token.aud << "\n";
        return false;
    }

    // 3. Захист від повтору через nonce (порівняння сталого часу)
    if (!constant_time_compare(token.nonce, expected_nonce)) {
        std::cerr << "Помилка OIDC: nonce не збігається зі значенням сесії!\n";
        return false;
    }

    // 4. Перевірка строку дії
    if (now >= (token.exp + max_clock_skew_sec)) {
        std::cerr << "Помилка OIDC: строк придатності токена вичерпано (exp)\n";
        return false;
    }

    // 5. Перевірка коректності часу видачі
    if (now < (token.iat - max_clock_skew_sec)) {
        std::cerr << "Помилка OIDC: час створення токена вказує на майбутнє (iat)\n";
        return false;
    }

    return true;
}

// Криптографічна перевірка підпису RSA-SHA256 (RS256) через OpenSSL EVP API
bool verify_rsa256_signature(const std::string& signing_input,
                             const std::vector<unsigned char>& raw_signature,
                             EVP_PKEY* public_key) {
    if (!public_key) return false;

    EVP_MD_CTX* md_ctx = EVP_MD_CTX_new();
    if (!md_ctx) return false;

    bool valid = false;
    if (EVP_DigestVerifyInit(md_ctx, nullptr, EVP_sha256(), nullptr, public_key) == 1) {
        if (EVP_DigestVerifyUpdate(md_ctx, signing_input.data(), signing_input.size()) == 1) {
            if (EVP_DigestVerifyFinal(md_ctx, raw_signature.data(), raw_signature.size()) == 1) {
                valid = true;
            }
        }
    }

    EVP_MD_CTX_free(md_ctx);
    return valid;
}
