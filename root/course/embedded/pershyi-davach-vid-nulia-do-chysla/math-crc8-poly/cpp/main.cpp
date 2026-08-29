#include <array>
#include <cstdint>
#include <cstdlib>
#include <format>
#include <iostream>
#include <span>
#include <string_view>

#include "crc8.hpp"
#include "errscan.hpp"

namespace {

// Ті самі вісім тактів на байт, що й у ручному розрахунку зі статті.
void show_manual_example()
{
    constexpr std::array<std::uint8_t, 2> data{0xBE, 0xEF};
    std::uint8_t reg = crc8::init;

    std::cout << std::format("Ручний розрахунок кадру 0xBE 0xEF (Init = 0x{:02X})\n",
                             crc8::init);
    for (const std::uint8_t byte : data) {
        std::cout << std::format("  байт 0x{:02X}: змішування 0x{:02X} ^ 0x{:02X} = 0x{:02X}\n",
                                 byte, reg, byte, static_cast<std::uint8_t>(reg ^ byte));
        const auto steps = crc8::trace(reg, byte);
        std::cout << "    такти:";
        for (const std::uint8_t s : steps) {
            std::cout << std::format(" 0x{:02X}", s);
        }
        reg = steps.back();
        std::cout << std::format("\n    залишок після байта: 0x{:02X}\n", reg);
    }
    std::cout << std::format("  CRC-8 = 0x{:02X}\n\n", reg);
}

void show_table_head()
{
    std::cout << "Перші 16 елементів таблиці на 256 байтів:\n ";
    for (const std::uint8_t v : std::span{crc8::table}.first(16)) {
        std::cout << std::format(" 0x{:02X}", v);
    }
    std::cout << "\n\n";
}

constexpr std::string_view describe(crc8::frame_error e) noexcept
{
    switch (e) {
    case crc8::frame_error::short_frame:
        return "кадр не з трьох байтів";
    case crc8::frame_error::crc_mismatch:
        return "CRC не збігся";
    }
    return "невідома причина";
}

void show_decode()
{
    constexpr std::array<std::uint8_t, 3> good{0xBE, 0xEF, 0x92};
    std::array<std::uint8_t, 3> broken = good;
    broken[1] ^= 0x01; // один спотворений біт даних

    for (const auto& frame : {good, broken}) {
        const auto value = crc8::word(frame);
        if (value) {
            std::cout << std::format("кадр {:02X} {:02X} {:02X} → слово 0x{:04X}\n",
                                     frame[0], frame[1], frame[2], *value);
        } else {
            std::cout << std::format("кадр {:02X} {:02X} {:02X} → відкинуто: {}\n",
                                     frame[0], frame[1], frame[2], describe(value.error()));
        }
    }
    std::cout << '\n';
}

// Три класи помилок, яких арифметична сума не бачить принципово.
void show_checksum_holes()
{
    constexpr std::array<std::uint8_t, 2> orig{0xBE, 0xEF};
    constexpr std::array<std::uint8_t, 2> swapped{0xEF, 0xBE};
    constexpr std::array<std::uint8_t, 2> compensated{0xBF, 0xEE}; // +1 і -1
    constexpr std::array<std::uint8_t, 3> zeroed{0xBE, 0x00, 0xEF};

    const auto line = [](std::string_view what, auto a, auto b) {
        std::cout << std::format("{:<20} сума 0x{:02X} проти 0x{:02X}, "
                                 "CRC 0x{:02X} проти 0x{:02X}\n",
                                 what, errscan::checksum(a), errscan::checksum(b),
                                 crc8::of(a), crc8::of(b));
    };

    line("Переставлені байти:", orig, swapped);
    line("Компенсовані біти:", orig, compensated);
    line("Вставлений 0x00:", orig, zeroed);
    std::cout << '\n';
}

void show_error_scan()
{
    constexpr std::array<std::uint16_t, 4> words{0xBEEF, 0x0000, 0xFFFF, 0x1234};

    std::cout << "Пропущені спотворення кадру (дані + байт захисту, 24 біти):\n"
                 "  слово   вид помилки       перевірено   повз CRC   повз суму\n";
    for (const std::uint16_t w : words) {
        for (int bits = 1; bits <= 3; ++bits) {
            const auto st = errscan::flips(w, bits);
            std::cout << std::format("  0x{:04X}  {}-бітові        {:10} {:10} {:11}\n",
                                     w, bits, st.checked, st.missed_crc, st.missed_sum);
        }
        const auto st = errscan::bursts(w, 8);
        std::cout << std::format("  0x{:04X}  пакети до 8 біт {:10} {:10} {:11}\n",
                                 w, st.checked, st.missed_crc, st.missed_sum);
    }
    std::cout << '\n';
}

// Таблиця й побітовий автомат мусять збігатися на всіх 65536 кадрах.
bool cross_check()
{
    for (unsigned w = 0; w < 65536u; ++w) {
        const std::array<std::uint8_t, 2> data{static_cast<std::uint8_t>(w >> 8),
                                               static_cast<std::uint8_t>(w)};
        if (crc8::of(data) != crc8::bitwise(data)) {
            std::cout << std::format("ПОМИЛКА: таблиця розійшлася з автоматом на 0x{:04X}\n", w);
            return false;
        }
    }
    return true;
}

} // namespace

int main()
{
    show_manual_example();
    show_table_head();
    show_decode();
    show_checksum_holes();
    show_error_scan();

    if (!cross_check()) {
        return EXIT_FAILURE;
    }
    std::cout << "Самоперевірка пройдена.\n";
    return EXIT_SUCCESS;
}
