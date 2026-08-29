// Демонстрація повного циклу: пробудження шини, перевірка блокування зон,
// підпис зовнішнього дайджеста ключем зі слота, сон (його робить деструктор).
//
// Збірка:  c++ -std=c++23 -Wall -Wextra -O2 src/*.cpp -o atecc-sign
// Запуск:  ./atecc-sign /dev/i2c-1 0 <64 шістнадцяткові символи дайджеста>
#include <array>
#include <charconv>
#include <cstdint>
#include <exception>
#include <format>
#include <iostream>
#include <optional>
#include <span>
#include <string_view>

#include "der.hpp"
#include "linux_i2c.hpp"
#include "secure_element.hpp"

namespace {

std::optional<std::array<std::uint8_t, atecc::kDigestSize>> parseDigest(std::string_view text)
{
    if (text.size() != atecc::kDigestSize * 2) {
        return std::nullopt;
    }

    std::array<std::uint8_t, atecc::kDigestSize> digest{};
    for (std::size_t i = 0; i < digest.size(); ++i) {
        const std::string_view byteText = text.substr(i * 2, 2);
        const auto [end, error] =
            std::from_chars(byteText.data(), byteText.data() + byteText.size(), digest[i], 16);
        if (error != std::errc{} || end != byteText.data() + byteText.size()) {
            return std::nullopt;
        }
    }
    return digest;
}

std::optional<std::uint8_t> parseSlot(std::string_view text)
{
    std::uint8_t slot = 0;
    const auto [end, error] = std::from_chars(text.data(), text.data() + text.size(), slot, 10);
    if (error != std::errc{} || end != text.data() + text.size() || slot > 15) {
        return std::nullopt;
    }
    return slot;
}

void printHex(std::string_view label, std::span<const std::uint8_t> bytes)
{
    std::string line(label);
    for (const std::uint8_t byte : bytes) {
        line += std::format("{:02x}", byte);
    }
    std::cout << line << '\n';
}

} // namespace

int main(int argc, char** argv)
{
    const std::span<char*> args(argv, static_cast<std::size_t>(argc));
    if (args.size() != 4) {
        std::cerr << std::format("вжиток: {} <шина> <слот 0..15> <дайджест-hex>\n", args[0]);
        return 2;
    }

    const auto slot = parseSlot(args[2]);
    if (!slot) {
        std::cerr << "слот має бути числом від 0 до 15\n";
        return 2;
    }
    const auto digest = parseDigest(args[3]);
    if (!digest) {
        std::cerr << "дайджест має бути рівно 64 шістнадцятковими символами\n";
        return 2;
    }

    try {
        atecc::LinuxI2cBus bus(args[1]);
        atecc::SecureElement chip(bus);

        if (const auto woken = chip.wake(); !woken) {
            std::cerr << std::format("пробудження: {} ({})\n", atecc::describe(woken.error()),
                                     atecc::describeStatus(chip.lastStatus()));
            return 1;
        }
        std::cout << "чип прокинувся\n";

        const auto locks = chip.lockState();
        if (!locks) {
            std::cerr << std::format("читання конфігурації: {} ({})\n",
                                     atecc::describe(locks.error()),
                                     atecc::describeStatus(chip.lastStatus()));
            return 1;
        }
        std::cout << std::format("зона конфігурації: {}, зона даних: {}\n",
                                 locks->configuration ? "заблокована" : "відкрита",
                                 locks->data ? "заблокована" : "відкрита");

        if (!locks->configuration || !locks->data) {
            // Незаблокований чип відхилить Sign — краще сказати це прямо, ніж
            // дати користувачеві розбирати код 0x0F.
            std::cerr << std::format("{}: пройдіть фабричне блокування (Lock)\n",
                                     atecc::describe(atecc::Error::NotLocked));
            return 1;
        }

        const auto signature = chip.signDigest(*slot, atecc::Digest(*digest));
        if (!signature) {
            std::cerr << std::format("підпис: {} ({})\n", atecc::describe(signature.error()),
                                     atecc::describeStatus(chip.lastStatus()));
            return 1;
        }

        printHex("R = ", std::span(*signature).first(32));
        printHex("S = ", std::span(*signature).last(32));
        printHex("DER = ", atecc::encodeDerSignature(*signature));
        return 0;
        // Деструктор chip надсилає команду сну, деструктор bus закриває шину.
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
