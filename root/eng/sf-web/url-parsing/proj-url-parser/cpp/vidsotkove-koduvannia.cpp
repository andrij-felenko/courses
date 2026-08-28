#include <string>
#include <string_view>
#include <sstream>
#include <iomanip>
#include <cctype>

class UrlCodec {
public:
    static bool is_unreserved(unsigned char c) noexcept {
        return (c >= 'A' && c <= 'Z') ||
               (c >= 'a' && c <= 'z') ||
               (c >= '0' && c <= '9') ||
               c == '-' || c == '.' || c == '_' || c == '~';
    }

    static std::string encode(std::string_view src) {
        static constexpr char hex[] = "0123456789ABCDEF";
        std::string dst;
        dst.reserve(src.size() * 3);

        for (unsigned char c : src) {
            if (is_unreserved(c)) {
                dst.push_back(static_cast<char>(c));
            } else {
                dst.push_back('%');
                dst.push_back(hex[c >> 4]);
                dst.push_back(hex[c & 0x0F]);
            }
        }
        return dst;
    }

    static std::string decode(std::string_view src) {
        std::string dst;
        dst.reserve(src.size());

        for (size_t i = 0; i < src.size(); ++i) {
            if (src[i] == '%' && i + 2 < src.size()) {
                auto hex_to_int = [](char h) -> int {
                    if (h >= '0' && h <= '9') return h - '0';
                    if (h >= 'A' && h <= 'F') return h - 'A' + 10;
                    if (h >= 'a' && h <= 'f') return h - 'a' + 10;
                    return -1;
                };

                int h1 = hex_to_int(src[i + 1]);
                int h2 = hex_to_int(src[i + 2]);
                if (h1 != -1 && h2 != -1) {
                    dst.push_back(static_cast<char>((h1 << 4) | h2));
                    i += 2;
                    continue;
                }
            }
            dst.push_back(src[i]);
        }
        return dst;
    }
};
