#include <string>
#include <vector>
#include <iomanip>
#include <sstream>
#include <random>
#include <algorithm>
#include <openssl/sha.h>

namespace totp {

struct BackupRecord {
    std::string hash_hex;
    bool used{false};
};

std::string hash_backup_code(std::string_view plain) {
    std::string clean;
    for (char c : plain) {
        if (c != '-' && c != ' ') {
            clean += static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        }
    }

    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(clean.data()), clean.size(), hash);

    std::ostringstream ss;
    for (unsigned char b : hash) {
        ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    return ss.str();
}

std::vector<std::string> generate_backup_codes(int count = 8) {
    std::random_device rd;
    std::vector<std::string> codes;
    codes.reserve(count);

    for (int i = 0; i < count; ++i) {
        std::ostringstream ss;
        for (int j = 0; j < 5; ++j) {
            ss << std::hex << std::setw(2) << std::setfill('0') << (rd() & 0xFF);
        }
        std::string raw = ss.str();
        codes.push_back(raw.substr(0, 5) + "-" + raw.substr(5));
    }
    return codes;
}

bool verify_and_consume(std::string_view input, std::vector<BackupRecord>& records) {
    std::string target_hash = hash_backup_code(input);
    for (auto& rec : records) {
        if (!rec.used && constant_time_equals(rec.hash_hex, target_hash)) {
            rec.used = true;
            return true;
        }
    }
    return false;
}

} // namespace totp
