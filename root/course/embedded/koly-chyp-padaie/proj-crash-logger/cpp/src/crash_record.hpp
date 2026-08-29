// Запис аварії в .noinit RAM. Читання назад повертає std::optional: або дамп
// цілий і перевірений CRC, або його немає — третього стану виклик не бачить.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace crash {

// Базовий кадр, який апаратура Cortex-M кладе на стек при вході у виняток.
struct CortexFrame {
    std::uint32_t r0;
    std::uint32_t r1;
    std::uint32_t r2;
    std::uint32_t r3;
    std::uint32_t r12;
    std::uint32_t lr;
    std::uint32_t pc;
    std::uint32_t psr;
};

enum class FpuFrame : std::uint32_t {
    None = 0,        // базовий кадр: співпроцесор не використовувався
    Saved = 1,       // розширений кадр, S0-S15 у стеку
    LazyPending = 2, // місце під S0-S15 виділено, вміст ще не збережено
};

// ⛔ ЖОДНИХ ініціалізаторів членів і жодного конструктора: варто дописати
// `= 0` бодай одному полю — і тип перестане бути тривіальним, стартовий код
// почне ініціалізувати об'єкт, а .noinit втратить сенс.
struct Record {
    std::uint32_t magic;
    std::uint32_t crash_count;
    std::uint32_t hfsr;
    std::uint32_t cfsr;
    std::uint32_t mmfar;
    std::uint32_t bfar;
    std::uint32_t shcsr;
    std::uint32_t exc_return;
    FpuFrame fpu;
    std::uint32_t fpscr;
    std::array<std::uint32_t, 16> s;
    CortexFrame frame;
    std::uint32_t crc; // мусить лишатися останнім: CRC рахується до нього
};

[[nodiscard]] std::uint32_t crc32(std::span<const std::byte> data) noexcept;

// frame — сирий покажчик, а не optional чи посилання: він може виявитися
// сміттям, і саме викликач вирішує, чи безпечно за ним читати.
void store(const CortexFrame* frame,
           std::uint32_t exc_return,
           FpuFrame fpu,
           std::span<const std::uint32_t> fpu_block) noexcept;

// Забирає дамп і гасить маркер: той самий звіт не повториться на наступному старті.
[[nodiscard]] std::optional<Record> take() noexcept;

// Лічильник живе окремо від дампу: скидання по сторожовому таймеру дампу не
// лишає, а рахувати такий перезапуск усе одно треба.
[[nodiscard]] std::uint32_t consecutive() noexcept;
std::uint32_t bump_counter() noexcept;
void clear_counter() noexcept;

} // namespace crash
