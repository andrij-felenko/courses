#include <iostream>
#include <string>

enum class ParseState {
    SearchPrefix,
    ReadHeader,
    ReadPayload
};

class IpdStreamParser {
    ParseState state = ParseState::SearchPrefix;
    std::string header_buffer;
    int payload_len = 0;
    int bytes_read = 0;

public:
    void processChar(char c) {
        if (state == ParseState::SearchPrefix) {
            if (c == '+') {
                header_buffer = "+";
                state = ParseState::ReadHeader;
            }
        } else if (state == ParseState::ReadHeader) {
            header_buffer += c;
            if (c == ':') {
                size_t last_comma = header_buffer.rfind(',');
                if (last_comma != std::string::npos) {
                    payload_len = std::stoi(header_buffer.substr(last_comma + 1));
                }
                bytes_read = 0;
                state = (payload_len > 0) ? ParseState::ReadPayload : ParseState::SearchPrefix;
            }
        } else if (state == ParseState::ReadPayload) {
            bytes_read++;
            if (bytes_read >= payload_len) {
                state = ParseState::SearchPrefix;
            }
        }
    }
};
