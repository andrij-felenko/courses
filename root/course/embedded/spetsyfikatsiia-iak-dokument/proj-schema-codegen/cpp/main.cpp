#include "telemetry_protocol.hpp"

#include <algorithm>
#include <array>
#include <cstdlib>
#include <format>
#include <iostream>
#include <string>

namespace {

constexpr std::array<std::uint8_t, 9> kCrcCheckVector{'1', '2', '3', '4', '5',
                                                      '6', '7', '8', '9'};
// Класичний вектор CRC-16/CCITT-FALSE перевіряється ще при компіляції.
static_assert(telemetry::crc16_ccitt(kCrcCheckVector) == 0x29B1);

// Тіло телеметрії, зібране руками: 8 байтів рівно за схемою.
constexpr std::array<std::uint8_t, 8> kTelemetryBody{
    0x92, 0x09,  // temp_raw     = 2450
    0x94, 0x27,  // pressure_raw = 10132
    0xE4, 0x0C,  // voltage_mv   = 3300
    0x01, 0x00   // flags, reserved
};

int failures = 0;

void dump(std::string_view label, std::span<const std::uint8_t> frame)
{
    std::string hex;
    for (std::uint8_t byte : frame) {
        hex += std::format("{:02X} ", byte);
    }
    std::cout << std::format("{:<16}{}  ({} байт)\n", label, hex, frame.size());
}

void expect_error(std::string_view what, std::span<const std::uint8_t> frame,
                  telemetry::ParseError want)
{
    const auto result = telemetry::parse(frame);
    const bool ok = !result && result.error() == want;
    if (!ok) {
        ++failures;
    }
    const std::string got =
        result ? std::string{"розібрано"} : std::string{telemetry::to_string(result.error())};
    std::cout << std::format("  {:<34} -> {:<20} {}\n", what, got, ok ? "ok" : "ПРОВАЛ");
}

std::span<std::uint8_t> copy_of(std::span<const std::uint8_t> src, std::span<std::uint8_t> dst)
{
    std::ranges::copy(src, dst.begin());
    return dst.first(src.size());
}

// Кує кадр із довільним заголовком: encode такого не збере — і добре, бо
// на дроті трапляється саме така кривизна. Сума рахується по тому, що
// ФІЗИЧНО лежить у буфері, тож кожен вектор перевіряє рівно одну ваду.
std::span<std::uint8_t> forge(std::span<std::uint8_t> out, std::uint8_t version,
                              std::uint8_t msg_id, std::uint8_t seq_id,
                              std::uint16_t declared_len, std::span<const std::uint8_t> payload)
{
    const std::size_t total = telemetry::kHeaderLen + payload.size() + telemetry::kFooterLen;
    out[0] = telemetry::kSof;
    out[1] = version;
    out[2] = msg_id;
    out[3] = seq_id;
    out[4] = static_cast<std::uint8_t>(declared_len & 0xFF);
    out[5] = static_cast<std::uint8_t>(declared_len >> 8);
    std::ranges::copy(payload, out.begin() + static_cast<std::ptrdiff_t>(telemetry::kHeaderLen));

    const std::uint16_t crc =
        telemetry::crc16_ccitt(out.subspan(1, telemetry::kHeaderLen - 1 + payload.size()));
    out[total - 3] = static_cast<std::uint8_t>(crc & 0xFF);
    out[total - 2] = static_cast<std::uint8_t>(crc >> 8);
    out[total - 1] = telemetry::kEof;
    return out.first(total);
}

void print_payload(const telemetry::Frame& frame)
{
    std::visit(
        [&frame](const auto& payload) {
            using T = std::decay_t<decltype(payload)>;
            if constexpr (std::is_same_v<T, telemetry::Telemetry>) {
                std::cout << std::format(
                    "seq=0x{:02X} T={:.2f} C p={:.1f} hPa U={} mV alert={} fault={}\n",
                    frame.seq_id, payload.temperature_c(), payload.pressure_hpa(),
                    payload.voltage_mv, payload.alert_active(), payload.sensor_fault());
            } else if constexpr (std::is_same_v<T, telemetry::SetConfig>) {
                std::cout << std::format("seq=0x{:02X} {} Гц, поріг {:.2f} C, прапорці 0x{:02X}\n",
                                         frame.seq_id, payload.sample_rate_hz,
                                         payload.alert_threshold_c(), payload.flags_enable);
            } else if constexpr (std::is_same_v<T, telemetry::Ack>) {
                std::cout << std::format("seq=0x{:02X} відповідь на 0x{:02X}: {}\n", frame.seq_id,
                                         payload.target_seq_id,
                                         telemetry::to_string(payload.status));
            } else {
                std::cout << std::format("seq=0x{:02X} ping\n", frame.seq_id);
            }
        },
        frame.payload);
}

// Зібрали, розібрали, надрукували — те саме коло, що й у прошивці.
void roundtrip(const telemetry::Frame& tx, std::span<std::uint8_t> storage)
{
    const auto wire = telemetry::encode(tx, storage);
    if (!wire) {
        std::cerr << std::format("кадр не зібрався: {}\n", telemetry::to_string(wire.error()));
        ++failures;
        return;
    }
    const auto parsed = telemetry::parse(*wire);
    if (!parsed) {
        std::cerr << std::format("розбір власного кадру: {}\n",
                                 telemetry::to_string(parsed.error()));
        ++failures;
        return;
    }
    print_payload(*parsed);
}

}  // namespace

int main()
{
    std::array<std::uint8_t, telemetry::kMaxFrame> storage{};
    std::array<std::uint8_t, telemetry::kMaxFrame> scratch{};

    const telemetry::Frame tx{
        .seq_id = 0x4A,
        .payload = telemetry::Telemetry{.temp_raw = 2450,       // 24.50 °C
                                        .pressure_raw = 10132,  // 1013.2 hPa
                                        .voltage_mv = 3300,
                                        .flags = telemetry::kFlagAlert,
                                        .reserved = 0x00}};

    const auto built = telemetry::encode(tx, storage);
    if (!built) {
        std::cerr << std::format("кадр не зібрався: {}\n", telemetry::to_string(built.error()));
        return EXIT_FAILURE;
    }
    const std::span<std::uint8_t> golden = *built;
    dump("Golden frame:", golden);

    const auto parsed = telemetry::parse(golden);
    if (!parsed) {
        std::cerr << std::format("розбір власного кадру: {}\n",
                                 telemetry::to_string(parsed.error()));
        return EXIT_FAILURE;
    }
    print_payload(*parsed);

    std::cout << "\nНегативні вектори:\n";

    expect_error("буфер коротший за мінімум", golden.first(4), telemetry::ParseError::InvalidLen);

    auto bad = copy_of(golden, scratch);
    bad[0] = 0x00;
    expect_error("сміття замість SOF", bad, telemetry::ParseError::InvalidSof);

    bad = copy_of(golden, scratch);
    bad.back() = 0x00;
    expect_error("обірваний EOF", bad, telemetry::ParseError::InvalidEof);

    bad = copy_of(golden, scratch);
    bad[telemetry::kHeaderLen] ^= 0x01;  // один перевернутий біт у навантаженні
    expect_error("перевернутий біт у payload", bad, telemetry::ParseError::InvalidCrc);

    // Заголовок обіцяє 8 байтів, у буфері їх 4 — ловимо ДО читання полів.
    expect_error("payload_len понад буфер",
                 forge(scratch, telemetry::kVersion, 0x20, 0x01, 8,
                       std::span{kTelemetryBody}.first(4)),
                 telemetry::ParseError::InvalidLen);

    // А тут довжина й буфер сходяться — не сходиться тип: telemetry це 8.
    expect_error("довжина не для цього типу",
                 forge(scratch, telemetry::kVersion, 0x20, 0x02, 5,
                       std::span{kTelemetryBody}.first(5)),
                 telemetry::ParseError::InvalidLen);

    expect_error("невідомий msg_id",
                 forge(scratch, telemetry::kVersion, 0x7F, 0x03, 2,
                       std::span{kTelemetryBody}.first(2)),
                 telemetry::ParseError::UnknownMsg);

    expect_error("чужа мажорна версія",
                 forge(scratch, 0x02, 0x20, 0x04, 8, kTelemetryBody),
                 telemetry::ParseError::UnsupportedVersion);

    // Від'ємна температура: 0xFEC8 = -312 = -3.12 °C.
    const telemetry::Frame cold{
        .seq_id = 0x4B,
        .payload = telemetry::Telemetry{.temp_raw = -312,
                                        .pressure_raw = 10000,
                                        .voltage_mv = 3290,
                                        .flags = telemetry::kFlagSensorFault,
                                        .reserved = 0x00}};
    const auto cold_frame = telemetry::encode(cold, storage).value();
    if (cold_frame[telemetry::kHeaderLen] != 0xC8 ||
        cold_frame[telemetry::kHeaderLen + 1] != 0xFE) {
        std::cerr << "знак на дроті лягає не так\n";
        return EXIT_FAILURE;
    }
    std::cout << "\n";
    print_payload(telemetry::parse(cold_frame).value());

    // Решта гілок switch-on — той самий кодек, інша альтернатива варіанта.
    roundtrip(telemetry::Frame{.seq_id = 0x10,
                               .payload = telemetry::SetConfig{.sample_rate_hz = 100,
                                                               .alert_threshold_raw = 8500,
                                                               .flags_enable = 0x03}},
              storage);
    roundtrip(telemetry::Frame{.seq_id = 0x11,
                               .payload = telemetry::Ack{.target_seq_id = 0x10,
                                                         .status = telemetry::StatusCode::Ok}},
              storage);
    roundtrip(telemetry::Frame{.seq_id = 0x12, .payload = telemetry::Ping{}}, storage);

    std::cout << (failures == 0 ? "\nусі вектори зійшлися\n" : "\nЄ РОЗБІЖНОСТІ\n");
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
