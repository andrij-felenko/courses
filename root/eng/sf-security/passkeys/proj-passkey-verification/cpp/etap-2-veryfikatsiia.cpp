#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <openssl/sha.h>

struct ParsedFlags {
    bool user_present;
    bool user_verified;
    bool backup_eligible;
    bool backup_state;
    bool has_attested_data;
};

struct ParsedAuthData {
    std::vector<uint8_t> rp_id_hash;
    ParsedFlags flags;
    uint32_t sign_count;
    std::string aaguid;
    std::vector<uint8_t> credential_id;
    std::vector<uint8_t> cose_public_key;
};

ParsedAuthData parse_auth_data(const std::vector<uint8_t>& buf) {
    if (buf.size() < 37) {
        throw std::runtime_error("authData too short (< 37 bytes)");
    }

    ParsedAuthData res;
    res.rp_id_hash.assign(buf.begin(), buf.begin() + 32);

    uint8_t f = buf[32];
    res.flags.user_present    = (f & 0x01) != 0;
    res.flags.user_verified   = (f & 0x04) != 0;
    res.flags.backup_eligible = (f & 0x08) != 0;
    res.flags.backup_state    = (f & 0x10) != 0;
    res.flags.has_attested_data = (f & 0x40) != 0;

    res.sign_count = (static_cast<uint32_t>(buf[33]) << 24) |
                     (static_cast<uint32_t>(buf[34]) << 16) |
                     (static_cast<uint32_t>(buf[35]) << 8)  |
                     (static_cast<uint32_t>(buf[36]));

    size_t offset = 37;
    if (res.flags.has_attested_data) {
        if (buf.size() < offset + 18) {
            throw std::runtime_error("Truncated attested credential data header");
        }

        // Форматуємо AAGUID (16 байтів) у стандартний рядок UUID
        char aaguid_hex[37];
        snprintf(aaguid_hex, sizeof(aaguid_hex),
                 "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x",
                 buf[offset], buf[offset+1], buf[offset+2], buf[offset+3],
                 buf[offset+4], buf[offset+5], buf[offset+6], buf[offset+7],
                 buf[offset+8], buf[offset+9], buf[offset+10], buf[offset+11],
                 buf[offset+12], buf[offset+13], buf[offset+14], buf[offset+15]);
        res.aaguid = aaguid_hex;
        offset += 16;

        uint16_t cred_id_len = (static_cast<uint16_t>(buf[offset]) << 8) | buf[offset + 1];
        offset += 2;

        if (buf.size() < offset + cred_id_len) {
            throw std::runtime_error("Truncated credential_id");
        }
        res.credential_id.assign(buf.begin() + offset, buf.begin() + offset + cred_id_len);
        offset += cred_id_len;

        // Залишок буфера — COSE Public Key
        res.cose_public_key.assign(buf.begin() + offset, buf.end());
    }

    return res;
}
