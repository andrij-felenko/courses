// trace.hpp — вивід діагностики через ITM/SWO.
//
// Ані iostream, ані printf: обробник збою працює на пошкодженому стеку,
// і ми не маємо права ані виділяти пам'ять, ані брати блокування.
// Тому потік тут власний, без стану й без буфера.
#pragma once

#include <cstdint>
#include <span>
#include <string_view>

namespace trace {

// Обгортка, що вибирає шістнадцяткове форматування без прапорців потоку.
struct Hex {
    std::uint32_t value;
};

class Writer {
public:
    Writer& operator<<(std::string_view text);
    Writer& operator<<(Hex value);
    Writer& operator<<(std::uint32_t value);
    Writer& operator<<(char symbol);
};

// Єдиний потік; стану не має, тому глобальний об'єкт безпечний навіть
// усередині винятку.
Writer& out();

// "  NAME = 0x00000000\n"
void reg(std::string_view name, std::uint32_t value);

// Опис одного прапорця регістра.
struct Flag {
    std::uint32_t    mask;
    std::string_view name;
    std::string_view text;
};

// Друкує лише встановлені прапорці; повертає їхню кількість.
std::size_t print_flags(std::span<const Flag> flags, std::uint32_t value);

}  // namespace trace
