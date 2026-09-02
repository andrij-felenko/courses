#pragma once

#include <span>
#include <string>
#include <string_view>

#include <termios.h>

namespace tty {

// Рядок таблиці відповідності: як прапорець зветься в stty і який це біт.
struct FlagBit {
    std::string_view stty;
    tcflag_t bit;
};

// Спецсимвол: ім'я аргументу stty й індекс у c_cc.
struct CharSlot {
    std::string_view stty;
    int index;
};

std::span<const FlagBit> input_flags() noexcept;
std::span<const FlagBit> output_flags() noexcept;
std::span<const FlagBit> control_flags() noexcept;
std::span<const FlagBit> local_flags() noexcept;
std::span<const CharSlot> special_chars() noexcept;

// Швидкість лінії в бодах; для BOTHER бере число прямо з c_ospeed.
unsigned long baud_rate(const termios& t) noexcept;

// Повний розбір у словах stty — те саме, що друкує `stty -a`.
std::string describe(const termios& t);

// Симптоми зламаного термінала з підказкою, чим лікувати.
// Порожній рядок означає, що типових поломок не видно.
std::string diagnose(const termios& t);

}  // namespace tty
