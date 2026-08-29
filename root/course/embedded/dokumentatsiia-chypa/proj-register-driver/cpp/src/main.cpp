/* Складання драйвера докупи: підняти USART1, відрапортувати ревізію
 * кремнію в лінію й далі відлунювати все, що прийшло.
 */
#include <cstdint>
#include <span>
#include <string_view>

#include "mmio/register.hpp"
#include "usart/silicon.hpp"
#include "usart/transmitter.hpp"

using namespace usart;

namespace {

/* Частота APB2 і швидкість лінії. Обидва числа беруться з налаштування
 * тактового дерева, а не вгадуються: помилка тут дає рівно ті самі
 * «ієрогліфи в терміналі», що й неправильний дільник. */
constexpr std::uint32_t pclk2_hz = 64'000'000;
constexpr std::uint32_t baudrate = 115'200;

/* Дозвіл переривання в контролері NVIC. Номер вектора USART1 — з таблиці
 * векторів переривань у Reference Manual. */
constexpr std::uintptr_t nvic_iser0_address = 0xE000'E100;
constexpr std::uint32_t  usart1_irq         = 27;

/* Драйвер живе в статичній пам'яті: конструктор лише запам'ятовує
 * посилання на блок, а стартовий код мікроконтролера викликає статичні
 * конструктори (__libc_init_array) до входу в main. */
Transmitter uart{usart1()};

void emit(std::string_view text) noexcept
{
    const std::span<const char> chars{text.data(), text.size()};
    /* Скільки саме байтів вийшло, тут не питаємо: єдиний споживач цього
     * рядка — людина в терміналі, обірваний рядок вона побачить сама. */
    (void)uart.send(std::as_bytes(chars));
}

} // namespace

/* Вектор переривання USART1 з таблиці векторів */
extern "C" void USART1_IRQHandler()
{
    /* Відлуння прямо в обробнику: один байт у вільний буфер лягає без
     * очікування. Довші відповіді звідси не шлють — довелося б крутити
     * цикл очікування з піднятим пріоритетом. */
    uart.on_interrupt([](std::byte value) noexcept { (void)uart.try_send(value); });
}

int main()
{
    if (!uart.configure(pclk2_hz, baudrate)) {
        /* Швидкість недосяжна від цієї шини: сказати про це нема чим —
         * зламаний саме той канал, яким доповідають про поломки. */
        for (;;) {
        }
    }

    switch (revision()) {
    case Revision::rev_a:
        emit("silicon Rev A: обхід дефекту TE увімкнено\r\n");
        break;
    case Revision::rev_b:
        emit("silicon Rev B: дефект TE усунено в кремнії\r\n");
        break;
    case Revision::unknown:
        emit("невідомий кремній: обхід дефекту TE увімкнено про всяк\r\n");
        break;
    }

    /* Дочекатися, поки рядок фізично вийде в лінію, і погасити TC: далі ми
     * дозволяємо переривання, і чужий TC у ньому лише збивав би. */
    (void)uart.flush();

    uart.enable_rx_irq();
    mmio::block<mmio::Register<std::uint32_t>>(nvic_iser0_address)
        .store(1u << usart1_irq);

    for (;;) {
        /* Помилки лінії знімає головний цикл, а не обробник: доповідь про
         * переповнення сама займає лінію, а робити це з переривання —
         * означає доповідати про затримку, стоячи в затримці. */
        const Isr errors = uart.take_errors();

        if (any(errors & Isr::ore)) { emit("overrun: байт втрачено\r\n"); }
        if (any(errors & Isr::nf))  { emit("noise: шум у лінії\r\n"); }
        if (any(errors & Isr::fe))  { emit("framing: збита швидкість або обірваний кадр\r\n"); }
        if (any(errors & Isr::pe))  { emit("parity: биті дані\r\n"); }
    }
}
