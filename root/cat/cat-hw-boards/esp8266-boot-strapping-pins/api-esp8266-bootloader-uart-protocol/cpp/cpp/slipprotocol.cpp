#include <vector>
#include <cstdint>

class SlipProtocol {
public:
    static constexpr uint8_t SLIP_END     = 0xC0;
    static constexpr uint8_t SLIP_ESC     = 0xDB;
    static constexpr uint8_t SLIP_ESC_END = 0xDC;
    static constexpr uint8_t SLIP_ESC_ESC = 0xDD;

    static std::vector<uint8_t> encodeFrame(const std::vector<uint8_t>& payload) {
        std::vector<uint8_t> encoded;
        encoded.reserve(payload.size() + 8);
        encoded.push_back(SLIP_END);

        for (uint8_t byte : payload) {
            if (byte == SLIP_END) {
                encoded.push_back(SLIP_ESC);
                encoded.push_back(SLIP_ESC_END);
            } else if (byte == SLIP_ESC) {
                encoded.push_back(SLIP_ESC);
                encoded.push_back(SLIP_ESC_ESC);
            } else {
                encoded.push_back(byte);
            }
        }
        encoded.push_back(SLIP_END);
        return encoded;
    }
};
