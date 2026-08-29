/* Типобезпечний доступ до апаратних регістрів.
 *
 * У C регістр — це volatile uint32_t, а маски — числа: ніщо не заважає
 * записати біт із ISR у ICR або переплутати CR1 з CR2, бо для компілятора
 * це все одне й те саме число. Тут регістр параметризовано типом його
 * вмісту, а набори бітів — це enum class. Тоді помилка «не той регістр»
 * або «не та маска» перестає бути помилкою часу виконання й ловиться
 * складанням, а не осцилографом.
 */
#pragma once

#include <concepts>
#include <cstdint>
#include <type_traits>

namespace mmio {

/* Позначка «цей enum — набір бітів». Оголошується спеціалізацією поруч із
 * самим enum, тож бітові операції з'являються лише там, де вони доречні. */
template <typename E>
struct is_flag_enum : std::false_type {};

template <typename E>
concept FlagEnum = std::is_enum_v<E> && is_flag_enum<E>::value;

template <FlagEnum E>
[[nodiscard]] constexpr std::underlying_type_t<E> raw(E value) noexcept
{
    return static_cast<std::underlying_type_t<E>>(value);
}

template <FlagEnum E>
[[nodiscard]] constexpr E operator|(E a, E b) noexcept
{
    return static_cast<E>(raw(a) | raw(b));
}

template <FlagEnum E>
[[nodiscard]] constexpr E operator&(E a, E b) noexcept
{
    return static_cast<E>(raw(a) & raw(b));
}

template <FlagEnum E>
constexpr E &operator|=(E &a, E b) noexcept
{
    a = a | b;
    return a;
}

/* Чи піднято хоч один із названих бітів */
template <FlagEnum E>
[[nodiscard]] constexpr bool any(E value) noexcept
{
    return raw(value) != 0;
}

/* Один апаратний регістр.
 *
 * Об'єкт цього типу неможливо ні створити, ні скопіювати: він існує лише
 * як частина блока за апаратною адресою. Читання й запис названі load і
 * store, а не оператором присвоєння, — щоб кожна транзакція на шині була
 * видима в тексті. Складеного `|=` тут навмисно немає: над регістром
 * стану це прихований read-modify-write, а саме він і губить події.
 */
template <typename T>
class Register {
public:
    Register() = delete;
    Register(const Register &) = delete;
    Register &operator=(const Register &) = delete;

    [[nodiscard]] T load() const noexcept { return value_; }

    void store(T value) noexcept { value_ = value; }

private:
    volatile T value_;
};

static_assert(sizeof(Register<std::uint32_t>) == 4);
static_assert(alignof(Register<std::uint32_t>) == 4);

/* Блок регістрів за фізичною адресою з карти пам'яті */
template <typename Block>
[[nodiscard]] inline Block &block(std::uintptr_t address) noexcept
{
    return *reinterpret_cast<Block *>(address);
}

/* Бар'єр синхронізації даних.
 *
 * Запис у периферію лягає в буфер запису й доїжджає до блока асинхронно.
 * Якщо погасити прапорець в останньому рядку обробника переривання й
 * одразу вийти, ядро встигне вийти раніше, ніж скидання добіжить шиною:
 * NVIC побачить прапорець піднятим і викличе обробник удруге на тій самій
 * події. dsb тримає ядро, поки транзакція не завершиться.
 */
inline void data_sync_barrier() noexcept
{
    asm volatile("dsb sy" ::: "memory");
}

} // namespace mmio
