// збірка: g++ -std=c++17 -O2 byte_to_fact.cpp -o byte_to_fact
#include <cstdint>
#include <cstdio>
#include <cstddef>
#include <functional>
#include <memory>
#include <string>
#include <utility>
#include <vector>

constexpr uint8_t STX            = 0xFE;   // початок кадру
constexpr uint8_t COMP_AUTOPILOT = 1;
constexpr uint8_t MSG_HEARTBEAT  = 0;
constexpr uint8_t MSG_ALT        = 33;     // урізаний родич GLOBAL_POSITION_INT

// CRC-16/MCRF4XX: дзеркальний поліном 0x1021, старт 0xFFFF, без фінального XOR.
inline void crc_step(uint8_t b, uint16_t &crc) {
    uint8_t t = static_cast<uint8_t>(b ^ (crc & 0xFF));
    t = static_cast<uint8_t>(t ^ (t << 4));
    crc = static_cast<uint16_t>((crc >> 8) ^ (t << 8) ^ (t << 3) ^ (t >> 4));
}

// Зібрати кадр — потрібно лише для того, щоб було чим годувати розбирач.
std::vector<uint8_t> pack(uint8_t seq, uint8_t sys, uint8_t comp, uint8_t msg,
                          const std::vector<uint8_t> &payload) {
    std::vector<uint8_t> f{STX, static_cast<uint8_t>(payload.size()), seq, sys, comp, msg};
    f.insert(f.end(), payload.begin(), payload.end());

    uint16_t crc = 0xFFFF;
    for (size_t i = 1; i < f.size(); ++i) crc_step(f[i], crc);   // усе, крім STX
    f.push_back(static_cast<uint8_t>(crc & 0xFF));
    f.push_back(static_cast<uint8_t>(crc >> 8));
    return f;
}
