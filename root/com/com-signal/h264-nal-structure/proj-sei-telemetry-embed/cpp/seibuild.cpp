// seibuild.cpp — те саме, але межі буфера рахує не людина.
// Збірка: c++ -O2 -std=c++20 -c seibuild.cpp
#include <array>
#include <cstdint>
#include <span>
#include <type_traits>
#include <vector>

// Згенеровано раз (uuidgen) і заморожено назавжди.
inline constexpr std::array<std::uint8_t, 16> kTeleUuid{
    0x8B,0x5F,0x1E,0x2A, 0x9C,0x44, 0x4D,0x71,
    0xA3,0x0E, 0x2F,0x18,0x77,0xC4,0x91,0x03};

struct Telemetry {
    std::int64_t  t_us{};                        // UTC, мікросекунди
    std::int32_t  lat_e7{}, lon_e7{}, alt_mm{};  // ×1e7, ×1e7, міліметри
    std::int16_t  yaw_cd{}, pitch_cd{}, roll_cd{};  // сантиградуси
    std::uint16_t seq{};                         // лічильник кадрів
};

using Bytes = std::vector<std::uint8_t>;

template <class T>
void put_be(Bytes& b, T v) {
    auto u = static_cast<std::make_unsigned_t<T>>(v);
    for (int i = sizeof(T) - 1; i >= 0; --i)
        b.push_back(static_cast<std::uint8_t>(u >> (8 * i)));
}

// payloadType і payloadSize: ланцюжок 0xFF, останній байт < 255
void put_varlen(Bytes& b, std::size_t v) {
    for (; v >= 255; v -= 255) b.push_back(0xFF);
    b.push_back(static_cast<std::uint8_t>(v));
}

// Крок 1: RBSP — тіло одиниці без заголовка NAL і без захисних байтів.
Bytes sei_rbsp(const Telemetry& t) {
    Bytes payload;
    payload.insert(payload.end(), kTeleUuid.begin(), kTeleUuid.end());
    put_be(payload, t.t_us);
    put_be(payload, t.lat_e7);
    put_be(payload, t.lon_e7);
    put_be(payload, t.alt_mm);
    put_be(payload, t.yaw_cd);
    put_be(payload, t.pitch_cd);
    put_be(payload, t.roll_cd);
    put_be(payload, t.seq);

    Bytes rbsp;
    put_varlen(rbsp, 5);                  // user_data_unregistered
    put_varlen(rbsp, payload.size());     // довжину каже сам вантаж
    rbsp.insert(rbsp.end(), payload.begin(), payload.end());
    rbsp.push_back(0x80);                 // rbsp_trailing_bits
    return rbsp;
}

// Крок 2: RBSP → байти потоку. Захист рахується від заголовка NAL.
Bytes sei_annexb(std::span<const std::uint8_t> rbsp) {
    Bytes out{0x00, 0x00, 0x00, 0x01, 0x06};   // стартовий код, nri = 0, тип 6
    int zeros = 0;
    for (std::uint8_t byte : rbsp) {
        if (zeros == 2 && byte <= 0x03) out.push_back(0x03);  // захисна трійка
        out.push_back(byte);
        zeros = (byte == 0x00) ? zeros + 1 : 0;
    }
    return out;
}
