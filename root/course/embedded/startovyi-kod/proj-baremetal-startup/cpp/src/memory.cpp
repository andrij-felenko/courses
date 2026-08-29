// memory.cpp — динамічна пам'ять: _sbrk для newlib і оператори new/delete.
//
// Купа росте від символу _end, тобто від першого вільного байта за глобальними
// змінними, угору назустріч стеку, який росте від _estack униз. Ця зустріч і є
// єдина справжня небезпека, тому стеля перевіряється двічі: статично за
// резервом _Min_Stack_Size і динамічно за поточним значенням покажчика стека.
//
// Усередині помилка їде в std::expected — відмова виражена типом, і забути її
// перевірити не вийде. Сирий контракт newlib ((void *)-1 плюс errno) лишається
// рівно в одній функції на межі: змінювати в ньому не можна нічого.

#include <algorithm>
#include <cerrno>
#include <cstddef>
#include <cstdint>
#include <cstdlib>
#include <expected>
#include <new>
#include <system_error>

#include "mcu/linker_symbols.hpp"
#include "mcu/scb.hpp"

namespace {

// Запас, який лишаємо стеку понад те, що він з'їв просто зараз: найглибший
// ланцюг викликів прошивки має вміститися в цей зазор.
constexpr std::size_t stack_guard = 256;

class Heap {
public:
    constexpr Heap() noexcept = default;

    std::expected<std::byte*, std::errc> grow(std::ptrdiff_t increment) noexcept
    {
        std::byte* const floor = mcu::linker::heap_start();
        if (top_ == nullptr) {
            top_ = floor;   // перший запит: купа починається за глобальними змінними
        }

        if (increment < 0) {
            // Повернення пам'яті. Нижче за _end опускатися не можна: там лежать
            // глобальні змінні.
            const auto back = static_cast<std::size_t>(-increment);
            if (static_cast<std::size_t>(top_ - floor) < back) {
                return std::unexpected(std::errc::invalid_argument);
            }
            top_ -= back;
            return top_ + back;
        }

        std::byte* const limit = ceiling();
        // Порівнюємо ЗАЛИШОК, а не суму: top_ + increment переповнилося б мовчки,
        // і перевірка пропустила б завідомо завеликий запит.
        if (limit <= top_ ||
            static_cast<std::size_t>(limit - top_) < static_cast<std::size_t>(increment)) {
            return std::unexpected(std::errc::not_enough_memory);
        }

        std::byte* const previous = top_;
        top_ += increment;
        return previous;
    }

    std::size_t used() const noexcept
    {
        return (top_ == nullptr)
                   ? 0
                   : static_cast<std::size_t>(top_ - mcu::linker::heap_start());
    }

private:
    // Нижча з двох стель. Статичний резерв каже, скільки стека ГАРАНТОВАНО, а
    // поточний SP ловить випадок, коли рекурсія вже з'їла більше за резерв.
    static std::byte* ceiling() noexcept
    {
        const auto sp = static_cast<std::size_t>(mcu::main_stack_pointer());
        std::byte* const dynamic =
            (sp < stack_guard) ? nullptr
                               : reinterpret_cast<std::byte*>(sp - stack_guard);
        return std::min(mcu::linker::heap_static_ceiling(), dynamic);
    }

    std::byte* top_{nullptr};
};

// constinit гарантує сталу ініціалізацію: об'єкт лягає в .bss і готовий ще до
// конструкторів глобальних об'єктів. Інакше перший же new у конструкторі
// іншого глобального об'єкта звернувся б до купи, якої ще не існує.
constinit Heap heap{};

}  // namespace

// Межа з newlib. Бібліотека кличе цю функцію за іменем і читає саме (void *)-1
// як відмову — тут контракт чужий, і виправляти в ньому нема чого.
extern "C" void* _sbrk(std::ptrdiff_t increment)
{
    const auto result = heap.grow(increment);
    if (!result) {
        errno = static_cast<int>(result.error());
        return reinterpret_cast<void*>(-1);
    }
    return *result;
}

// Скільки байтів купи роздано просто зараз — для перевірок у прикладному коді
// й для погляду під налагоджувачем.
namespace mcu::linker {
std::size_t heap_used() noexcept { return heap.used(); }
}  // namespace mcu::linker

// ── Оператори new і delete ───────────────────────────────────────────────────
// Прошивка збирається з -fno-exceptions, тож кинути std::bad_alloc нема чим:
// відмова купи спиняє ядро точкою зупину. Це не заглушка, а свідоме рішення —
// продовжувати з нульовим покажчиком гірше, ніж стати рівно на місці збою.

void* operator new(std::size_t size)
{
    void* const block = std::malloc(size != 0 ? size : 1);
    if (block == nullptr) {
        mcu::halt();
    }
    return block;
}

void* operator new[](std::size_t size) { return ::operator new(size); }

void* operator new(std::size_t size, const std::nothrow_t&) noexcept
{
    return std::malloc(size != 0 ? size : 1);
}

void* operator new[](std::size_t size, const std::nothrow_t& tag) noexcept
{
    return ::operator new(size, tag);
}

void operator delete(void* block) noexcept { std::free(block); }
void operator delete[](void* block) noexcept { std::free(block); }

// Розмірні форми: компілятор кличе саме їх, коли розмір відомий на місці
// виклику. Без цих визначень лінкер узяв би версії з libsupc++, а вони тягнуть
// за собою обробку винятків.
void operator delete(void* block, std::size_t) noexcept { std::free(block); }
void operator delete[](void* block, std::size_t) noexcept { std::free(block); }
