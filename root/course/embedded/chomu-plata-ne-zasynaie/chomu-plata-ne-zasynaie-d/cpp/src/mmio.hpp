// mmio.hpp — типобезпечний доступ до регістрів.
//
// Регістр тут — об'єкт, а не макрос: адреса відома на етапі компіляції,
// а звертання лишається рівно одним volatile-читанням чи записом.
#pragma once

#include <cstdint>

namespace hal {

using Word = std::uint32_t;

[[nodiscard]] constexpr Word bit(unsigned index) noexcept
{
    return Word{1} << index;
}

[[nodiscard]] constexpr Word maskOf(unsigned width, unsigned shift) noexcept
{
    return ((Word{1} << width) - Word{1}) << shift;
}

class Mmio {
public:
    explicit constexpr Mmio(std::uintptr_t address) noexcept : address_{address} {}

    [[nodiscard]] Word load() const noexcept { return *pointer(); }

    void store(Word value) const noexcept { *pointer() = value; }

    void modify(Word clear, Word set) const noexcept { store((load() & ~clear) | set); }

    void setBits(Word mask) const noexcept { modify(0U, mask); }

    void clearBits(Word mask) const noexcept { modify(mask, 0U); }

    [[nodiscard]] bool anyOf(Word mask) const noexcept { return (load() & mask) != 0U; }

    [[nodiscard]] Word field(unsigned width, unsigned shift) const noexcept
    {
        return (load() >> shift) & ((Word{1} << width) - Word{1});
    }

    void writeField(unsigned width, unsigned shift, Word value) const noexcept
    {
        modify(maskOf(width, shift), (value << shift) & maskOf(width, shift));
    }

private:
    [[nodiscard]] volatile Word* pointer() const noexcept
    {
        return reinterpret_cast<volatile Word*>(address_);
    }

    std::uintptr_t address_;
};

// Обмежене очікування прапорця: раб, що завис, не має права
// підвісити прошивку назавжди.
template <typename Predicate>
[[nodiscard]] bool spinUntil(Predicate ready, std::uint32_t limit) noexcept
{
    for (std::uint32_t attempt = 0; attempt < limit; ++attempt) {
        if (ready()) {
            return true;
        }
    }
    return false;
}

} // namespace hal
