#include <vector>
#include <string>
#include <string_view>
#include <stdexcept>
#include <random>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <cstdint>

namespace totp {

inline constexpr std::string_view BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";

std::string generate_base32_secret(std::size_t byte_length = 20) {
    std::random_device rd;
    std::vector<std::uint8_t> buffer(byte_length);
    for (auto& b : buffer) {
        b = static_cast<std::uint8_t>(rd());
    }

    std::string result;
    std::uint32_t value = 0;
    int bits = 0;
    for (std::uint8_t b : buffer) {
        value = (value << 8) | b;
        bits += 8;
        while (bits >= 5) {
            result += BASE32_ALPHABET[(value >> (bits - 5)) & 31];
            bits -= 5;
        }
    }
    if (bits > 0) {
        result += BASE32_ALPHABET[(value << (5 - bits)) & 31];
    }
    return result;
}

std::vector<std::uint8_t> decode_base32(std::string_view input) {
    std::vector<std::uint8_t> bytes;
    std::uint32_t value = 0;
    int bits = 0;
    for (char c : input) {
        if (c == ' ' || c == '-' || c == '=') continue;
        char upper = static_cast<char>(std::toupper(static_cast<unsigned char>(c)));
        auto pos = BASE32_ALPHABET.find(upper);
        if (pos == std::string_view::npos) {
            throw std::runtime_error("Недійсний символ Base32");
        }
        value = (value << 5) | static_cast<std::uint32_t>(pos);
        bits += 5;
        if (bits >= 8) {
            bytes.push_back(static_cast<std::uint8_t>((value >> (bits - 8)) & 0xFF));
            bits -= 8;
        }
    }
    return bytes;
}

} // namespace totp
