// utf8_sanitize.cpp — Ідіоматичний валідатор UTF-8 та нормалізатор (C++20).
// Збірка: g++ -std=c++20 -Wall -Wextra -O2 utf8_sanitize.cpp -o utf8_sanitize

#include <iostream>
#include <vector>
#include <span>
#include <cstdint>
#include <string_view>
#include <optional>
#include <system_error>

enum class Utf8Error {
    Ok = 0,
    InvalidByte,
    Overlong,
    Surrogate,
    OutOfRange,
    Truncated
};

struct DecodeResult {
    uint32_t codepoint;
    size_t bytes_consumed;
};

class Utf8Validator {
public:
    static std::optional<DecodeResult> decode_next(std::span<const uint8_t> buffer, Utf8Error &err) {
        if (buffer.empty()) {
            err = Utf8Error::Truncated;
            return std::nullopt;
        }

        const uint8_t b0 = buffer[0];
        if (b0 < 0x80) {
            err = Utf8Error::Ok;
            return DecodeResult{ .codepoint = b0, .bytes_consumed = 1 };
        }

        if ((b0 & 0xE0) == 0xC0) {
            if (buffer.size() < 2) { err = Utf8Error::Truncated; return std::nullopt; }
            const uint8_t b1 = buffer[1];
            if ((b1 & 0xC0) != 0x80) { err = Utf8Error::InvalidByte; return std::nullopt; }

            uint32_t cp = ((b0 & 0x1F) << 6) | (b1 & 0x3F);
            if (cp < 0x80) { err = Utf8Error::Overlong; return std::nullopt; }

            err = Utf8Error::Ok;
            return DecodeResult{ .codepoint = cp, .bytes_consumed = 2 };
        }

        if ((b0 & 0xF0) == 0xE0) {
            if (buffer.size() < 3) { err = Utf8Error::Truncated; return std::nullopt; }
            const uint8_t b1 = buffer[1];
            const uint8_t b2 = buffer[2];
            if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80) {
                err = Utf8Error::InvalidByte;
                return std::nullopt;
            }

            uint32_t cp = ((b0 & 0x0F) << 12) | ((b1 & 0x3F) << 6) | (b2 & 0x3F);
            if (cp < 0x0800) { err = Utf8Error::Overlong; return std::nullopt; }
            if (cp >= 0xD800 && cp <= 0xDFFF) { err = Utf8Error::Surrogate; return std::nullopt; }

            err = Utf8Error::Ok;
            return DecodeResult{ .codepoint = cp, .bytes_consumed = 3 };
        }

        if ((b0 & 0xF8) == 0xF0) {
            if (buffer.size() < 4) { err = Utf8Error::Truncated; return std::nullopt; }
            const uint8_t b1 = buffer[1];
            const uint8_t b2 = buffer[2];
            const uint8_t b3 = buffer[3];
            if ((b1 & 0xC0) != 0x80 || (b2 & 0xC0) != 0x80 || (b3 & 0xC0) != 0x80) {
                err = Utf8Error::InvalidByte;
                return std::nullopt;
            }

            uint32_t cp = ((b0 & 0x07) << 18) | ((b1 & 0x3F) << 12) | ((b2 & 0x3F) << 6) | (b3 & 0x3F);
            if (cp < 0x10000) { err = Utf8Error::Overlong; return std::nullopt; }
            if (cp > 0x10FFFF) { err = Utf8Error::OutOfRange; return std::nullopt; }

            err = Utf8Error::Ok;
            return DecodeResult{ .codepoint = cp, .bytes_consumed = 4 };
        }

        err = Utf8Error::InvalidByte;
        return std::nullopt;
    }

    static void sanitize_stream(std::istream &in, std::ostream &out) {
        std::vector<uint8_t> buffer(std::istreambuf_iterator<char>(in), {});
        if (buffer.empty()) return;

        size_t pos = 0;
        // Пропуск UTF-8 BOM
        if (buffer.size() >= 3 && buffer[0] == 0xEF && buffer[1] == 0xBB && buffer[2] == 0xBF) {
            pos = 3;
        }

        bool prev_cr = false;
        while (pos < buffer.size()) {
            std::span<const uint8_t> remaining{buffer.data() + pos, buffer.size() - pos};
            Utf8Error err = Utf8Error::Ok;
            auto res = decode_next(remaining, err);

            if (!res) {
                std::cerr << "Помилка валідації UTF-8 на зміщенні " << pos << '\n';
                break;
            }

            if (res->codepoint == '\r') {
                out.put('\n');
                prev_cr = true;
            } else if (res->codepoint == '\n') {
                if (!prev_cr) {
                    out.put('\n');
                }
                prev_cr = false;
            } else {
                prev_cr = false;
                out.write(reinterpret_cast<const char*>(buffer.data() + pos), res->bytes_consumed);
            }
            pos += res->bytes_consumed;
        }
    }
};

int main() {
    std::ios_base::sync_with_stdio(false);
    Utf8Validator::sanitize_stream(std::cin, std::cout);
    return 0;
}
