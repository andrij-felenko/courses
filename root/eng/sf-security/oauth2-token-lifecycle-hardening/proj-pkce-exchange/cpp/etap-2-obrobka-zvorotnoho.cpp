#include <cstring>
#include <openssl/crypto.h>

// Порівняння двох рядків у сталий час для захисту від таймінг-атак
bool constant_time_compare(std::string_view a, std::string_view b) {
    if (a.size() != b.size()) {
        return false;
    }
    return CRYPTO_memcmp(a.data(), b.data(), a.size()) == 0;
}

// Формування тіла запиту для POST /token
std::string format_token_exchange_body(const std::string& authorization_code,
                                       const std::string& code_verifier,
                                       const std::string& redirect_uri,
                                       const std::string& client_id,
                                       const std::string& client_secret = "") {
    std::ostringstream ss;
    ss << "grant_type=authorization_code"
       << "&code=" << authorization_code
       << "&redirect_uri=" << redirect_uri
       << "&client_id=" << client_id
       << "&code_verifier=" << code_verifier;

    // Для конфіденційних клієнтів додаємо секрет
    if (!client_secret.empty()) {
        ss << "&client_secret=" << client_secret;
    }
    return ss.str();
}
