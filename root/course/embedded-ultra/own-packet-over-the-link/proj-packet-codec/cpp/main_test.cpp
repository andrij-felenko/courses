// ============================================================================
// main_test.cpp — Тестування стійкості автомата мовою C++
// ============================================================================
#include <array>
#include <cassert>
#include <span>
#include <vector>

int main() {
    using namespace TelemetryProtocol;

    StreamParser parser;
    std::array<std::uint8_t, 128> txBuffer{};
    std::array<std::uint8_t, 4> dummyPayload{0x11, 0x22, 0x33, 0x44};

    // 1. Серіалізація валідного кадру
    std::size_t frameLen = serialize(0x02, 10, dummyPayload, txBuffer);
    assert(frameLen == 11);

    // 2. Декодування без завад
    Packet rxPacket{};
    ParserResult res{ParserResult::NeedMoreBytes};
    for (std::size_t i = 0; i < frameLen; ++i) {
        res = parser.consumeByte(txBuffer[i], rxPacket);
    }
    assert(res == ParserResult::PacketReady);
    assert(rxPacket.msg_id == 0x02);
    assert(rxPacket.seq == 10);
    assert(rxPacket.len == 4);

    // 3. Інверсія біта -> очікуємо ErrorCrc
    txBuffer[6] ^= 0x01;
    for (std::size_t i = 0; i < frameLen; ++i) {
        res = parser.consumeByte(txBuffer[i], rxPacket);
    }
    assert(res == ParserResult::ErrorCrc);

    return 0;
}
