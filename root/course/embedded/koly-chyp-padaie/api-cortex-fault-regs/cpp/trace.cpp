#include "trace.hpp"

#include "stm32f4xx.h"  // CMSIS: ITM_SendChar()

namespace trace {
namespace {

// ITM_SendChar() сам перевіряє, чи ввімкнено трасування. Без відладчика
// символ тихо гине — діагностика не має права вішати прошивку очікуванням.
void put(char symbol)
{
    if (symbol == '\n') {
        static_cast<void>(ITM_SendChar('\r'));
    }
    static_cast<void>(ITM_SendChar(static_cast<std::uint32_t>(static_cast<unsigned char>(symbol))));
}

}  // namespace

Writer& Writer::operator<<(std::string_view text)
{
    for (char symbol : text) {
        put(symbol);
    }
    return *this;
}

Writer& Writer::operator<<(char symbol)
{
    put(symbol);
    return *this;
}

Writer& Writer::operator<<(Hex value)
{
    constexpr std::string_view digits = "0123456789ABCDEF";

    *this << "0x";
    for (unsigned shift = 28; ; shift -= 4) {
        put(digits[(value.value >> shift) & 0xFu]);
        if (shift == 0) {
            break;
        }
    }
    return *this;
}

Writer& Writer::operator<<(std::uint32_t value)
{
    char buffer[10];
    std::size_t length = 0;

    do {
        buffer[length++] = static_cast<char>('0' + (value % 10u));
        value /= 10u;
    } while (value != 0u);

    while (length-- > 0) {
        put(buffer[length]);
    }
    return *this;
}

Writer& out()
{
    static Writer writer;
    return writer;
}

void reg(std::string_view name, std::uint32_t value)
{
    out() << "  " << name << " = " << Hex{value} << '\n';
}

std::size_t print_flags(std::span<const Flag> flags, std::uint32_t value)
{
    std::size_t shown = 0;

    for (const Flag& flag : flags) {
        if ((value & flag.mask) == 0u) {
            continue;
        }
        out() << "    * " << flag.name << " — " << flag.text << '\n';
        ++shown;
    }
    return shown;
}

}  // namespace trace
