// flash.hpp — вимога до носія, записана концептом.
//
// Черга не тримає покажчиків на функції й не знає жодного драйвера:
// вона шаблон, а FlashDevice каже, що саме має вміти тип-параметр.
// Диспетчеризація зникає в компіляції — на Cortex-M це той рідкісний
// випадок, коли абстракція справді безкоштовна.
//
// Правила NOR, які концепт не ховає, бо на них тримається вся черга:
//   програмування лише гасить біти (1 -> 0), підняти назад може тільки
//   стирання сектора; стертий сектор — суцільні 0xFF.
#pragma once

#include <concepts>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

namespace sfq {

enum class FlashError {
    Io,          // шина мовчить або мікросхема відкинула команду
    Timeout,     // операція не вклалась у паспортний час
    OutOfRange,  // адреса поза кристалом
    NotAligned,  // стирання не з межі сектора
};

struct Geometry {
    std::uint32_t sector_size{};  // найменша одиниця стирання
    std::uint32_t page_size{};    // найбільший неподільний запис
    std::uint32_t capacity{};
};

using FlashResult = std::expected<void, FlashError>;

template <class D>
concept FlashDevice = requires(D& dev, const D& cdev, std::uint32_t addr,
                               std::span<std::byte> out, std::span<const std::byte> in) {
    { dev.read(addr, out) } -> std::same_as<FlashResult>;
    { dev.program(addr, in) } -> std::same_as<FlashResult>;
    { dev.erase_sector(addr) } -> std::same_as<FlashResult>;
    { cdev.geometry() } -> std::same_as<Geometry>;
};

}  // namespace sfq
