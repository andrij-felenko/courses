/* Драйвер передавача USART: уся логіка поверх регістрової карти.
 *
 * Помилки повертаються через std::expected, а не кодом -1 і глобальною
 * змінною: результат неможливо мовчки проігнорувати, а часткова невдача
 * несе із собою кількість відданих байтів прямо в типі помилки.
 */
#pragma once

#include <atomic>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>

#include "usart/registers.hpp"
#include "usart/silicon.hpp"

namespace usart {

enum class Error : std::uint8_t {
    baud_out_of_range, // потрібна швидкість недосяжна від цієї шини
    timeout,           // передавач не звільнив буфер за відведений час
};

/* Обрив посеред буфера: коду помилки самого по собі мало — треба знати,
 * де саме воно стало, інакше повторна відправка дублює вже відданий шмат. */
struct SendFailure {
    Error       error;
    std::size_t sent;
};

class Transmitter {
public:
    explicit Transmitter(Block &regs) noexcept : regs_(regs) {}

    /* Апаратний блок один на систему: копії драйвера означали б двох
     * господарів одного заліза. */
    Transmitter(const Transmitter &) = delete;
    Transmitter &operator=(const Transmitter &) = delete;

    /* Дільник швидкості, UE|TE, обхід дефекту за ревізією кремнію */
    [[nodiscard]] std::expected<void, Error> configure(std::uint32_t pclk_hz,
                                                       std::uint32_t baud) noexcept;

    void enable_rx_irq() noexcept;

    [[nodiscard]] std::expected<void, Error> send(std::byte value) noexcept;

    /* Довжина їде разом із даними, окремим аргументом її не загубиш */
    [[nodiscard]] std::expected<std::size_t, SendFailure>
    send(std::span<const std::byte> data) noexcept;

    /* Відправка без очікування: байт іде, лише якщо буфер уже вільний.
     * Саме це й потрібно з обробника переривання, де крутити цикл не можна. */
    [[nodiscard]] bool try_send(std::byte value) noexcept;

    /* Дочекатися, поки останній байт фізично вийде в лінію, і погасити TC */
    [[nodiscard]] std::expected<void, Error> flush() noexcept;

    /* Забрати накопичені помилки лінії — і відкладені обробником, і ті,
     * що стоять у ISR зараз. Викликається з головного циклу. */
    [[nodiscard]] Isr take_errors() noexcept;

    /* Обробник переривання блока.
     *
     * Sink — шаблонний параметр, а не вказівник на функцію: лямбда з
     * захопленням підставляється в тіло без непрямого виклику, і в
     * обробнику не лишається жодного стрибка за таблицею.
     */
    template <std::invocable<std::byte> Sink>
    void on_interrupt(Sink &&sink) noexcept
    {
        /* Знімок стану робиться один раз на вхід. Два звернення до ISR у
         * сусідніх рядках побачили б різне, і рішення розійшлися б. */
        const Isr state = regs_.isr.load();
        Icr pending = Icr::none;

        if (const Isr errors = state & Isr::errors; any(errors)) {
            /* Гасимо тут-таки — інакше ORE тримає лінію переривання
             * піднятою й обробник крутиться без кінця, — а сам факт
             * відкладаємо: доповідь про помилку сама займає лінію. */
            pending |= to_clear(errors);
            sticky_errors_.fetch_or(raw(errors), std::memory_order_relaxed);
        }

        if (any(state & Isr::rxne)) {
            /* Читання RDR скидає RXNE апаратно — саме тому в ICR для
             * нього немає біта. Байт треба забрати в будь-якому разі,
             * інакше наступний символ дасть переповнення. */
            sink(static_cast<std::byte>(regs_.rdr.load() & 0xFFu));
        }

        if (any(state & Isr::tc)) {
            pending |= Icr::tccf;
        }

        if (any(pending)) {
            /* Один запис у ICR на всі прапорці разом; бар'єр — усередині
             * clear(), і без нього NVIC викликав би нас удруге. */
            clear(regs_, pending);
        } else {
            /* Прапорців не гасили, але RDR читали — буфер шини спільний,
             * тож бар'єр перед виходом потрібен однаково. */
            mmio::data_sync_barrier();
        }
    }

private:
    [[nodiscard]] std::expected<void, Error> wait_for(Isr flag) noexcept;
    void settle_after_te() noexcept;

    Block                     &regs_;
    std::uint32_t              spin_limit_ = 0;

    /* Спільне поле головного циклу й обробника переривання. std::atomic,
     * а не заборона переривань довкола кожного дотику: fetch_or на ядрі
     * з LDREX/STREX — це та сама пара інструкцій, тільки без ризику
     * забути ввімкнути переривання на ранньому виході. */
    std::atomic<std::uint32_t> sticky_errors_{0};
};

} // namespace usart
