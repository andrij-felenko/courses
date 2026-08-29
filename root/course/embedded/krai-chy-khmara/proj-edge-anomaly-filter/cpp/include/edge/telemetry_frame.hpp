#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

#include "edge/anomaly_detector.hpp"

namespace edge {

/*
 * Бінарний кадр для радіоканалу (LoRa, NB-IoT, BLE), молодший байт уперед.
 *
 *   зсув  розмір  поле
 *   0     1       0x7E                        магічний байт
 *   1     1       версія<<4 | прапорці        версія 1; біт 0 — відмова давача
 *   2     1       дія (Action)
 *   3     4       мітка часу, мс
 *   7     4       значення, float
 *   11    4       середнє, float
 *   15    4       СКВ, float
 *   19    2       z, беззнакове Q8.8 (0xFFFF — насичення)
 *   21    1       довжина знімка, 0..32
 *   22    2*N     знімок: (x - середнє)*100, int16; -32768 — вибірка невалідна
 *   ..    2       CRC-16/CCITT-FALSE по всіх попередніх байтах
 *
 * Знімок їде у фіксованій комі відносно середнього, а не масивом float:
 * 64 байти замість 128. На LoRa SF12 кожні зайві 50 байт — це зайва секунда
 * в ефірі й зайвий мілі-ампер-час з батареї.
 */

inline constexpr std::size_t frame_header_size = 22;
inline constexpr std::size_t max_frame_size = frame_header_size + 2 * snapshot_depth + 2;
inline constexpr std::int16_t snapshot_invalid = -32768;

/// Готове сховище під кадр: клас на стеку задачі або в BSS, ніякої купи.
using FrameStorage = std::array<std::byte, max_frame_size>;

[[nodiscard]] std::uint16_t crc16_ccitt(std::span<const std::byte> data) noexcept;

/// Пакує звіт і знімок у out. Порожній optional — буфер замалий:
/// кадр, обрізаний посередині, гірший за неспроби його відправити.
/// Повертається саме та частина out, що заповнена, — довжину не треба
/// передавати окремим аргументом і не можна з нею розсинхронізуватися.
[[nodiscard]] std::optional<std::span<const std::byte>>
encode(const Report& report,
       std::span<const float> snapshot,
       std::span<std::byte> out) noexcept;

}  // namespace edge
