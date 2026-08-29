// Сканування кільця секторів на старті: де голова, де хвіст, який
// наступний номер кадру. Покажчики у Flash не зберігаються взагалі —
// їх відновлює цей прохід із самих кадрів.
#pragma once

#include <algorithm>
#include <array>
#include <concepts>
#include <cstdint>
#include <expected>
#include <span>

#include "sf/frame.hpp"

namespace sf {

struct IoError {
    std::uint32_t addr{};
    std::size_t   len{};
};

// Сканеру потрібне лише читання й геометрія. Що там за носієм — SPI NOR,
// FRAM чи образ у пам'яті — його не обходить, тому вимога виражена
// концептом, а не віртуальним інтерфейсом: жодної таблиці віртуальних
// функцій у прошивці й повне вбудовування виклику читання.
template <class F>
concept FlashArea = requires(const F& flash, std::uint32_t addr, std::span<std::byte> dst) {
    { flash.read(addr, dst) } -> std::same_as<std::expected<void, IoError>>;
    { flash.sector_size() } -> std::convertible_to<std::uint32_t>;
    { flash.sector_count() } -> std::convertible_to<std::uint32_t>;
};

struct SectorInfo {
    bool          used{};       // сектор містить хоч один валідний кадр
    bool          damaged{};    // перший же кадр не пройшов перевірку
    bool          torn{};       // валідні кадри є, але останній обірвано
    std::uint32_t frames{};
    std::uint32_t first_seq{};
    std::uint32_t last_seq{};
    std::uint32_t end_offset{}; // кінець останнього валідного кадру
};

struct QueueState {
    bool          empty{true};       // жодного валідного кадру в кільці
    std::uint32_t head_sector{};     // сектор, у який піде наступний кадр
    std::uint32_t head_offset{};     // зсув у ньому
    std::uint32_t next_seq{1};       // номер, який отримає наступний кадр
    std::uint32_t tail_sector{};     // найстаріший сектор із даними
    std::uint32_t tail_seq{};        // номер найстарішого кадру
    std::uint32_t valid_frames{};    // скільки кадрів пережило знеструмлення
    std::uint32_t damaged_sectors{}; // сектори з битим першим кадром
    bool          torn_tail{};       // запис у голові обірвано на півдорозі
};

// Кадр ніколи не перетинає межу сектора — інакше одне стирання рвало б
// два записи, а сканер не міг би йти посекторно. Тому сектор читається
// незалежно від сусідів, і пошкодження локалізоване.
template <FlashArea F>
[[nodiscard]] std::expected<SectorInfo, IoError>
scan_sector(const F& flash, std::uint32_t index)
{
    std::array<std::byte, kMaxFrame> buffer{};
    SectorInfo info{};

    const std::uint32_t sector_size = flash.sector_size();
    const std::uint32_t base        = index * sector_size;
    std::uint32_t       offset      = 0;

    while (offset + kHeaderSize + kCrcSize <= sector_size) {
        const std::size_t want = std::min<std::size_t>(sector_size - offset, buffer.size());
        const auto chunk = std::span{buffer}.first(want);
        if (auto io = flash.read(base + offset, chunk); !io) {
            return std::unexpected(io.error());
        }

        const auto frame = parse(chunk);
        if (frame) {
            if (info.frames == 0) {
                info.first_seq = frame->header.seq;
            }
            info.last_seq = frame->header.seq;
            ++info.frames;
            offset += static_cast<std::uint32_t>(frame->total);
            continue;
        }

        // Стерта область — нормальний кінець сектора. Будь-яка інша
        // помилка означає, що живлення зникло під час запису або
        // комірки деградували; за таким місцем сканування не йде:
        // далі в секторі лежить сміття з попереднього циклу.
        if (frame.error() != FrameError::Erased) {
            (info.frames == 0 ? info.damaged : info.torn) = true;
        }
        break;
    }

    info.end_offset = offset;
    info.used       = info.frames > 0;
    return info;
}

template <FlashArea F>
[[nodiscard]] std::expected<QueueState, IoError> recover(const F& flash)
{
    QueueState state{};
    SectorInfo head{};
    bool       found = false;

    for (std::uint32_t index = 0; index < flash.sector_count(); ++index) {
        const auto info = scan_sector(flash, index);
        if (!info) {
            return std::unexpected(info.error());
        }

        if (info->damaged) {
            ++state.damaged_sectors;
        }
        if (!info->used) {
            continue;
        }

        state.valid_frames += info->frames;

        if (!found) {
            found             = true;
            head              = *info;
            state.head_sector = index;
            state.tail_sector = index;
            state.tail_seq    = info->first_seq;
            continue;
        }

        // Голова — сектор із найбільшим номером кадру, хвіст — із
        // найменшим. Порядок індексів тут ні до чого: після обороту
        // кільця голова має менший індекс, ніж хвіст.
        if (seq_after(info->last_seq, head.last_seq)) {
            head              = *info;
            state.head_sector = index;
        }
        if (seq_after(state.tail_seq, info->first_seq)) {
            state.tail_sector = index;
            state.tail_seq    = info->first_seq;
        }
    }

    if (!found) {
        return state; // порожнє кільце: пишемо з нуля, seq починається з 1
    }

    state.empty       = false;
    state.head_offset = head.end_offset;
    state.torn_tail   = head.torn;

    // Голова стає строго за останнім валідним кадром. Обірваний хвіст
    // запису нікуди не дівається — його накриють наступні байти після
    // чергового стирання сектора, а в мережу він не потрапить ніколи.
    state.next_seq = head.last_seq + 1;
    if (state.next_seq == 0) {
        state.next_seq = 1; // нуль лишаємо як «номера немає»
    }

    return state;
}

} // namespace sf
