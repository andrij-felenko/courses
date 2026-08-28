#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <openssl/evp.h>
#include <openssl/sha.h>
#include <openssl/x509.h>

bool verify_ecdsa_signature(
    const std::vector<uint8_t>& auth_data,
    const std::vector<uint8_t>& client_data_json,
    const std::vector<uint8_t>& signature_der,
    const std::vector<uint8_t>& public_key_spki_der
) {
    // 1. Обчислюємо SHA-256 від clientDataJSON
    unsigned char client_hash[SHA256_DIGEST_LENGTH];
    SHA256(client_data_json.data(), client_data_json.size(), client_hash);

    // 2. Формуємо SignedData = authData || SHA-256(clientDataJSON)
    std::vector<uint8_t> signed_data = auth_data;
    signed_data.insert(signed_data.end(), client_hash, client_hash + SHA256_DIGEST_LENGTH);

    // 3. Імпортуємо відкритий ключ OpenSSL з формату DER SPKI
    const unsigned char* p = public_key_spki_der.data();
    EVP_PKEY* pkey = d2i_PUBKEY(nullptr, &p, static_cast<long>(public_key_spki_der.size()));
    if (!pkey) {
        throw std::runtime_error("Failed to decode SPKI public key");
    }

    // 4. Ініціалізуємо контекст перевірки підпису
    EVP_MD_CTX* md_ctx = EVP_MD_CTX_new();
    bool is_valid = false;

    if (EVP_DigestVerifyInit(md_ctx, nullptr, EVP_sha256(), nullptr, pkey) == 1) {
        int res = EVP_DigestVerify(
            md_ctx,
            signature_der.data(), signature_der.size(),
            signed_data.data(), signed_data.size()
        );
        is_valid = (res == 1);
    }

    EVP_MD_CTX_free(md_ctx);
    EVP_PKEY_free(pkey);
    return is_valid;
}
