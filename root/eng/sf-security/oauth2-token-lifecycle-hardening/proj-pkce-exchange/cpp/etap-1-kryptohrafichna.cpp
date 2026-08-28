#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <openssl/sha.h>
#include <openssl/rand.h>

// Безпечне перетворення двійкових даних у рядок Base64URL без паддингу '='
std::string base64url_encode(const unsigned char* data, size_t length) {
    static const char lookup[] =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
    std::string out;
    out.reserve(((length + 2) / 3) * 4);

    size_t i = 0;
    while (i < length) {
        uint32_t octet_a = i < length ? data[i++] : 0;
        uint32_t octet_b = i < length ? data[i++] : 0;
        uint32_t octet_c = i < length ? data[i++] : 0;

        uint32_t triple = (octet_a << 16) + (octet_b << 8) + octet_c;

        out.push_back(lookup[(triple >> 18) & 0x3F]);
        out.push_back(lookup[(triple >> 12) & 0x3F]);
        if (i > length + 1) break;
        out.push_back(lookup[(triple >> 6) & 0x3F]);
        if (i > length) break;
        out.push_back(lookup[triple & 0x3F]);
    }
    return out;
}

// Отримання високоентропійного псевдовипадкового рядка
std::string generate_secure_random_string(size_t num_bytes) {
    std::vector<unsigned char> buffer(num_bytes);
    if (RAND_bytes(buffer.data(), static_cast<int>(num_bytes)) != 1) {
        throw std::runtime_error("Критична помилка генератора OpenSSL RAND_bytes");
    }
    return base64url_encode(buffer.data(), buffer.size());
}

struct OidcAuthorizationContext {
    std::string verifier;
    std::string challenge;
    std::string state;
    std::string nonce;
};

// Генерація повного набору параметрів безпеки для старту сесії
OidcAuthorizationContext create_oidc_context() {
    OidcAuthorizationContext ctx;
    // 32 байти дають рівно 43 символи base64url (мінімальний дозволений розмір за RFC 7636)
    ctx.verifier = generate_secure_random_string(32);
    ctx.state    = generate_secure_random_string(24);
    ctx.nonce    = generate_secure_random_string(24);

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(ctx.verifier.data()),
           ctx.verifier.size(), hash);

    ctx.challenge = base64url_encode(hash, SHA256_DIGEST_LENGTH);
    return ctx;
}

// Формування кінцевої адреси для HTTP-перенаправлення 302
std::string build_authorization_url(const std::string& auth_endpoint,
                                    const std::string& client_id,
                                    const std::string& redirect_uri,
                                    const std::string& scope,
                                    const OidcAuthorizationContext& ctx) {
    std::ostringstream ss;
    ss << auth_endpoint << "?"
       << "response_type=code"
       << "&client_id=" << client_id
       << "&redirect_uri=" << redirect_uri
       << "&scope=" << scope
       << "&state=" << ctx.state
       << "&nonce=" << ctx.nonce
       << "&code_challenge=" << ctx.challenge
       << "&code_challenge_method=S256";
    return ss.str();
}
