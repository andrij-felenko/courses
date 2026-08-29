#pragma once

#include <cstdint>
#include <span>
#include <string_view>
#include <variant>

#include "hmac_sha256.hpp"

namespace secure {

/* Кадр: заголовок 18 Б | навантаження N Б | тег 32 Б.
 * Заголовок і навантаження разом ідуть під HMAC. */
inline constexpr std::uint16_t kFrameMagic    = 0xA55AU;
inline constexpr std::size_t   kHeaderSize    = 18;
inline constexpr std::size_t   kTagSize       = Sha256::kDigestSize;
inline constexpr std::size_t   kFrameOverhead = kHeaderSize + kTagSize;

/* Розмір вікна дорівнює розрядності маски: більше в неї не влізе. */
inline constexpr std::uint64_t kReplayWindowSize = 64;

enum class ParseError : std::uint8_t {
    BufferTooSmall,
    InvalidMagic,
    PayloadMismatch,
    AuthFailed,
    TimestampExpired,
    ReplayDetected
};

[[nodiscard]] std::string_view to_string(ParseError error) noexcept;

/* Розібрана команда. payload дивиться ВСЕРЕДИНУ вхідного буфера: копії немає,
 * тож дані дійсні рівно доти, доки живий буфер приймача. */
struct Command {
    std::uint8_t  type{};
    std::uint64_t seq{};
    std::uint32_t timestamp{};
    std::span<const std::uint8_t> payload{};
};

/*
 * Прошивки збирають із -fno-exceptions, тож помилку віддаємо значенням.
 * std::expected був би тут точнішим, але він зʼявився аж у C++23 — variant
 * дає ту саму гарантію "або результат, або помилка, третього немає".
 */
using ParseResult = std::variant<Command, ParseError>;

/*
 * Ковзне вікно захисту від повтору: старший прийнятий лічильник і маска на
 * 64 позиції нижче за нього (біт 0 — сам max_seq). Шістнадцять байтів стану
 * на канал, жодного виділення памʼяті.
 */
class ReplayWindow {
public:
    constexpr ReplayWindow() noexcept = default;

    /* true — лічильник ще не бачили і він не застарілий. Стану не змінює. */
    [[nodiscard]] constexpr bool check(std::uint64_t seq) const noexcept {
        if (seq == 0) {
            return false;               /* нуль зарезервовано під "вікно порожнє" */
        }
        if (seq > max_seq_) {
            return true;                /* новий рекорд — точно ще не бачили */
        }
        const std::uint64_t diff = max_seq_ - seq;
        if (diff >= kReplayWindowSize) {
            return false;               /* старіший за все вікно: памʼяті вже немає */
        }
        return (bitmap_ & (1ULL << diff)) == 0;   /* біт стоїть — це дублікат */
    }

    /* Фіксувати лише ПІСЛЯ успішної перевірки тегу: інакше підроблений кадр
     * із величезним лічильником зсуне вікно й відсіче справжні команди. */
    constexpr void commit(std::uint64_t seq) noexcept {
        if (seq > max_seq_) {
            const std::uint64_t shift = seq - max_seq_;
            if (shift >= kReplayWindowSize) {
                bitmap_ = 1ULL;         /* стрибок довший за вікно — маска марна */
            } else {
                /* Зсув на 64 — невизначена поведінка, тому гілка вище. */
                bitmap_ = (bitmap_ << shift) | 1ULL;
            }
            max_seq_ = seq;
        } else {
            const std::uint64_t diff = max_seq_ - seq;
            if (diff < kReplayWindowSize) {
                bitmap_ |= (1ULL << diff);   /* запізнілий кадр усередині вікна */
            }
        }
    }

    [[nodiscard]] constexpr std::uint64_t max_sequence() const noexcept { return max_seq_; }

private:
    std::uint64_t max_seq_{0};
    std::uint64_t bitmap_{0};
};

/*
 * Стан одного захищеного каналу. Ключ не копіюється — канал тримає span,
 * тож ключ мусить жити не менше за канал (зазвичай це масив у Flash).
 */
class SecureChannel {
public:
    SecureChannel(std::span<const std::uint8_t> key, std::uint32_t max_drift_s) noexcept
        : key_(key), max_drift_s_(max_drift_s) {}

    /* Повний конвеєр приймача: рамка -> тег -> час -> вікно -> команда. */
    [[nodiscard]] ParseResult parse(std::span<const std::uint8_t> frame,
                                    std::uint32_t now_s) noexcept;

    [[nodiscard]] const ReplayWindow& window() const noexcept { return window_; }

private:
    std::span<const std::uint8_t> key_;
    std::uint32_t max_drift_s_;
    ReplayWindow  window_{};
};

}  // namespace secure
