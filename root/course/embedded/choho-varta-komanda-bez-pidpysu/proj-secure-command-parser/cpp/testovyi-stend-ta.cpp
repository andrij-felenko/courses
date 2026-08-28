#include <iostream>
#include <vector>

int main() {
    using namespace embedded::security;

    std::array<uint8_t, 16> secret_key{'m','c','u','_','s','e','c','r','e','t','_','k','e','y','1'};
    CommandVerifier verifier(secret_key);

    std::vector<uint8_t> frame(sizeof(FrameHeader) + 2 + TagSize);
    FrameHeader hdr{FrameMagic, 0x01, 0x00, 100, 1700000000U, 2};
    std::memcpy(frame.data(), &hdr, sizeof(FrameHeader));
    frame[sizeof(FrameHeader)] = 0x00;
    frame[sizeof(FrameHeader) + 1] = 0x5A;

    /* Обчислення тестового тегу */
    uint32_t acc = 0x811C9DC5U;
    for (auto b : secret_key) acc = (acc ^ b) * 0x01000193U;
    for (size_t i = 0; i < sizeof(FrameHeader) + 2; ++i) acc = (acc ^ frame[i]) * 0x01000193U;
    std::memcpy(frame.data() + sizeof(FrameHeader) + 2, &acc, sizeof(acc));

    // Тест 1: Валідний пакет
    auto res1 = verifier.parse(frame, 1700000005U, 10);
    std::cout << "Test 1 (Valid Frame): " << (res1.has_value() ? "OK" : "FAILED") << "\n";

    // Тест 2: Повтор
    auto res2 = verifier.parse(frame, 1700000006U, 10);
    std::cout << "Test 2 (Replay Attack): " 
              << (res2.get_error() == ParseError::ReplayDetected ? "BLOCKED (OK)" : "FAILED") << "\n";

    return 0;
}
