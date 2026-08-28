#include <cstdint>
#include <vector>
#include <string_view>
#include <span>

namespace ndef {

class RecordBuilder {
public:
    static std::vector<uint8_t> create_uri(uint8_t prefix_code, std::string_view url_body, bool is_first = true, bool is_last = true) {
        size_t payload_len = 1 + url_body.size();
        bool is_short = (payload_len <= 255);

        size_t header_size = 1 + 1 + (is_short ? 1 : 4) + 1;
        std::vector<uint8_t> buffer;
        buffer.reserve(header_size + payload_len);

        uint8_t flags = 0x01; // TNF = Well-Known
        if (is_first) flags |= 0x80;
        if (is_last)  flags |= 0x40;
        if (is_short) flags |= 0x10;

        buffer.push_back(flags);
        buffer.push_back(1); // Type Length ('U')

        if (is_short) {
            buffer.push_back(static_cast<uint8_t>(payload_len));
        } else {
            buffer.push_back(static_cast<uint8_t>(payload_len >> 24));
            buffer.push_back(static_cast<uint8_t>(payload_len >> 16));
            buffer.push_back(static_cast<uint8_t>(payload_len >> 8));
            buffer.push_back(static_cast<uint8_t>(payload_len & 0xFF));
        }

        buffer.push_back('U');
        buffer.push_back(prefix_code);

        buffer.insert(buffer.end(), url_body.begin(), url_body.end());

        return buffer;
    }
};

} // namespace ndef
