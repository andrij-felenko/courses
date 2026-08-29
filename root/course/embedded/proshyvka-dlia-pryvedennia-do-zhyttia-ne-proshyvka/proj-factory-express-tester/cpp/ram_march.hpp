#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

#include "fct.hpp"
#include "hal.hpp"

// March C- на виділеному статичному буфері. Стек і таблиця векторів у тест
// не потрапляють: інверсна маска по них означала б негайний HardFault.

namespace fct {

inline constexpr std::size_t kRamTestWords = 1024;
inline constexpr std::uint32_t kZeros = 0x00000000u;
inline constexpr std::uint32_t kOnes = 0xFFFFFFFFu;

// volatile обов'язковий: без нього компілятор викине «зайві» читання,
// і марш перевірятиме оптимізатор, а не кремній.
using Cell = volatile std::uint32_t;

template <std::size_t Words>
class MarchC {
public:
    using Memory = std::span<Cell, Words>;

    // Індекс комірки, що не витримала фазу; nullopt — фаза чиста.
    [[nodiscard]] static std::optional<std::size_t> run(Memory mem) noexcept
    {
        fill(mem, kZeros);                        // ↕(w0)
        hal::watchdog_kick();

        if (auto bad = up(mem, kZeros, kOnes)) {  // ⇑(r0,w1)
            return bad;
        }
        hal::watchdog_kick();
        if (auto bad = up(mem, kOnes, kZeros)) {  // ⇑(r1,w0)
            return bad;
        }
        hal::watchdog_kick();
        if (auto bad = down(mem, kZeros, kOnes)) {  // ⇓(r0,w1)
            return bad;
        }
        hal::watchdog_kick();
        if (auto bad = down(mem, kOnes, kZeros)) {  // ⇓(r1,w0)
            return bad;
        }
        hal::watchdog_kick();
        return verify(mem, kZeros);               // ↕(r0)
    }

    // Назва фази, у якій сидить дефект, — для звіту оператору.
    [[nodiscard]] static constexpr std::string_view phase_hint(std::size_t) noexcept
    {
        return "March C-: комірка не витримала прохід";
    }

private:
    static void fill(Memory mem, std::uint32_t value) noexcept
    {
        for (auto& cell : mem) {
            cell = value;
        }
    }

    static std::optional<std::size_t> up(Memory mem, std::uint32_t expect,
                                         std::uint32_t write) noexcept
    {
        for (std::size_t i = 0; i < mem.size(); ++i) {
            if (mem[i] != expect) {
                return i;
            }
            mem[i] = write;
        }
        return std::nullopt;
    }

    static std::optional<std::size_t> down(Memory mem, std::uint32_t expect,
                                           std::uint32_t write) noexcept
    {
        for (std::size_t i = mem.size(); i > 0; --i) {
            if (mem[i - 1] != expect) {
                return i - 1;
            }
            mem[i - 1] = write;
        }
        return std::nullopt;
    }

    static std::optional<std::size_t> verify(Memory mem, std::uint32_t expect) noexcept
    {
        for (std::size_t i = 0; i < mem.size(); ++i) {
            if (mem[i] != expect) {
                return i;
            }
        }
        return std::nullopt;
    }
};

inline Outcome test_ram_march() noexcept
{
    static Cell buffer[kRamTestWords]{};

    // Переривання замасковані на весь марш: обробник, що торкнеться буфера
    // чи просто затримає прохід, зіпсує картину дефектів.
    const IrqMask mask;
    const auto bad = MarchC<kRamTestWords>::run(
        std::span<Cell, kRamTestWords>{buffer, kRamTestWords});

    if (bad) {
        return fail(Error::Fail, "March C-: SAF / TF / CF у комірці",
                    static_cast<std::int32_t>(*bad), "word");
    }
    return pass("March C- пройдено повністю",
                static_cast<std::int32_t>(kRamTestWords), "words");
}

}  // namespace fct
