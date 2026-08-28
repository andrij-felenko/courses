#include <string>
#include <vector>
#include <chrono>
#include <random>
#include <openssl/rand.h>

struct RegistrationOptions {
    std::string rp_id;
    std::string rp_name;
    std::string user_id_b64;
    std::string user_name;
    std::string user_display_name;
    std::string challenge_b64;
    uint32_t timeout_ms;
    std::string resident_key;
    std::string user_verification;
};

// Допоміжне кодування у Base64URL без знаків вирівнювання '='
std::string to_base64url(const unsigned char* data, size_t len) {
    static const char tbl[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
    std::string res;
    res.reserve(((len + 2) / 3) * 4);
    for (size_t i = 0; i < len; i += 3) {
        uint32_t b = (data[i] << 16) | 
                     ((i + 1 < len ? data[i + 1] : 0) << 8) | 
                     (i + 2 < len ? data[i + 2] : 0);
        res.push_back(tbl[(b >> 18) & 0x3F]);
        res.push_back(tbl[(b >> 12) & 0x3F]);
        if (i + 1 < len) res.push_back(tbl[(b >> 6) & 0x3F]);
        if (i + 2 < len) res.push_back(tbl[b & 0x3F]);
    }
    return res;
}

RegistrationOptions generate_registration_options(
    const std::string& user_id,
    const std::string& email,
    const std::string& display_name,
    const std::string& rp_id
) {
    unsigned char challenge_bytes[32];
    RAND_bytes(challenge_bytes, sizeof(challenge_bytes));

    RegistrationOptions opt;
    opt.rp_id = rp_id;
    opt.rp_name = "Acme Cloud Platform";
    opt.user_id_b64 = to_base64url(reinterpret_cast<const unsigned char*>(user_id.data()), user_id.size());
    opt.user_name = email;
    opt.user_display_name = display_name;
    opt.challenge_b64 = to_base64url(challenge_bytes, sizeof(challenge_bytes));
    opt.timeout_ms = 60000;
    opt.resident_key = "required";
    opt.user_verification = "preferred";
    return opt;
}
