#include "constant_time.hpp"

#include <atomic>

namespace ct {

bool verify(std::span<const std::uint8_t> a, std::span<const std::uint8_t> b) noexcept
{
    // Довжина — не секрет: розмір тегу відомий із формату кадру,
    // тому ранній вихід тут нічого не видає.
    if (a.size() != b.size()) {
        return false;
    }

    // volatile навмисно. Без нього компілятор має право помітити, що
    // результат циклу визначений уже на першому ненульовому diff, і
    // зібрати з нього ранній вихід — тобто повернути ту саму витікаючу
    // поведінку memcmp, яку ми тут прибираємо.
    const volatile std::uint8_t* left = a.data();
    const volatile std::uint8_t* right = b.data();

    std::uint8_t diff = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        diff = static_cast<std::uint8_t>(diff | (left[i] ^ right[i]));
    }

    return diff == 0;
}

void wipe(std::span<std::uint8_t> buffer) noexcept
{
    volatile std::uint8_t* bytes = buffer.data();
    for (std::size_t i = 0; i < buffer.size(); ++i) {
        bytes[i] = 0;
    }
    // Бар'єр не пускає компілятор переставити чи злити ці записи
    // з тим, що робиться після звільнення буфера.
    std::atomic_signal_fence(std::memory_order_seq_cst);
}

}  // namespace ct
