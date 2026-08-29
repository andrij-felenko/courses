#include "usart/transmitter.hpp"

namespace usart {
namespace {

/* Найменший дільник при 16-кратному передискретизуванні: менше — приймач
 * не встигає набрати вибірок на біт. Стеля — розрядність самого BRR.
 * Обидва числа з Reference Manual, не з голови. */
constexpr std::uint32_t brr_min = 16;
constexpr std::uint32_t brr_max = 0xFFFF;

/* Верхня межа очікування, виражена в прохідках циклу.
 *
 * Це не годинник, а страховка від вічного зависання: точний час дала б
 * системна лічилка тактів, але на етапі підняття периферії її ще немає.
 * Рахуємо грубо й із запасом: символ — це десять бітів плюс пауза, одна
 * прохідка коштує щонайменше кілька тактів ядра. */
[[nodiscard]] constexpr std::uint32_t spin_limit_for(std::uint32_t pclk_hz,
                                                     std::uint32_t baud) noexcept
{
    return (pclk_hz / baud) * 12 + 64;
}

} // namespace

std::expected<void, Error> Transmitter::configure(std::uint32_t pclk_hz,
                                                  std::uint32_t baud) noexcept
{
    if (baud == 0 || pclk_hz == 0) {
        return std::unexpected(Error::baud_out_of_range);
    }

    /* Дільник із округленням до найближчого: відкидання дробової частини
     * дає похибку швидкості, і на довгому кадрі приймач з'їжджає з біта. */
    const std::uint32_t brr = (pclk_hz + baud / 2) / baud;
    if (brr < brr_min || brr > brr_max) {
        /* Мовчки записати обрізане значення означає віддати в лінію
         * сміття й шукати причину осцилографом. */
        return std::unexpected(Error::baud_out_of_range);
    }

    spin_limit_ = spin_limit_for(pclk_hz, baud);

    /* Ревізію питаємо тут і зберігати її нема потреби: TE піднімається
     * рівно один раз, і дефект стосується тільки цієї миті. */
    const bool te_workaround = needs_te_workaround(revision());

    /* Порядок важливий: швидкість налаштовуємо, поки блок вимкнений —
     * запис у BRR при піднятому UE документація лишає невизначеним. */
    regs_.cr1.store(Cr1::none);
    regs_.brr.store(brr);

    /* Повний запис, а не читання-модифікація: після скидання решта бітів
     * CR1 нульова, і RMW тут лише додав би вікно для гонки без користі. */
    regs_.cr1.store(Cr1::ue | Cr1::te);

    if (te_workaround) {
        settle_after_te();
    }

    /* Прапорці, що лишилися від попереднього сеансу або від сміття на
     * лінії, поки блок піднімався, гасимо до першої відправки. */
    clear(regs_, Icr::errors | Icr::tccf);

    return {};
}

void Transmitter::settle_after_te() noexcept
{
    /* Обхід дефекту Rev A з Errata Sheet: між установленням TE й першим
     * записом у TDR має пройти щонайменше один такт периферійної шини,
     * інакше перший стартовий біт виходить некоректної тривалості.
     *
     * Зворотне читання регістра того самого блока — це повна транзакція
     * читання на APB: вона не може початися раніше за попередній запис у
     * той самий блок і сама коштує не менше такту шини. Порожній nop тут
     * не годиться — ядро тактується швидше за APB, і такт ядра це лише
     * частка такту шини. */
    [[maybe_unused]] const Cr1 readback = regs_.cr1.load();
    mmio::data_sync_barrier();
}

std::expected<void, Error> Transmitter::wait_for(Isr flag) noexcept
{
    std::uint32_t spin = spin_limit_;

    while (!any(regs_.isr.load() & flag)) {
        if (spin == 0) {
            /* Знятий тактовий сигнал блока, зупинений налагоджувачем
             * периферійний домен — причин багато, і всі вони не привід
             * висіти в циклі до перезавантаження сторожовим таймером. */
            return std::unexpected(Error::timeout);
        }
        --spin;
    }
    return {};
}

void Transmitter::enable_rx_irq() noexcept
{
    /* Тут читання-модифікація доречні й безпечні: CR1 — регістр керування,
     * апаратура сама в нього не пише, конкурента в цій гонці немає. */
    regs_.cr1.store(regs_.cr1.load() | Cr1::rxneie);
}

bool Transmitter::try_send(std::byte value) noexcept
{
    if (!any(regs_.isr.load() & Isr::txe)) {
        return false;
    }
    regs_.tdr.store(std::to_integer<std::uint32_t>(value) & tdr_mask);
    return true;
}

std::expected<void, Error> Transmitter::send(std::byte value) noexcept
{
    if (auto ready = wait_for(Isr::txe); !ready) {
        return ready;
    }

    /* Один 32-бітний запис у TDR. Старші біти апаратура відкидає сама,
     * але маскуємо явно — щоб ширина слова даних була видима в коді. */
    regs_.tdr.store(std::to_integer<std::uint32_t>(value) & tdr_mask);
    return {};
}

std::expected<std::size_t, SendFailure>
Transmitter::send(std::span<const std::byte> data) noexcept
{
    std::size_t sent = 0;

    for (const std::byte value : data) {
        if (auto written = send(value); !written) {
            return std::unexpected(SendFailure{written.error(), sent});
        }
        ++sent;
    }
    return sent;
}

std::expected<void, Error> Transmitter::flush() noexcept
{
    if (auto done = wait_for(Isr::tc); !done) {
        return done;
    }

    /* TC гасимо записом одиниці в TCCF регістра ICR. Класичне
     * isr &= ~tc зняло б заразом і RXNE, який апаратура могла підняти
     * між читанням і зворотним записом, — і прийнятий байт зник би
     * разом із перериванням, якого через це не станеться. */
    clear(regs_, Icr::tccf);
    return {};
}

Isr Transmitter::take_errors() noexcept
{
    /* Спершу забираємо відкладене обробником, потім знімаємо живе. Те, що
     * обробник підніме між цими двома кроками, він сам і погасить у ICR, а
     * до нас воно приїде наступним колом — втратити помилку не виходить. */
    std::uint32_t bits = sticky_errors_.exchange(0, std::memory_order_acquire);

    /* Одне читання ISR: два підряд дали б два різні знімки стану, і
     * погасити ми могли б не те, про що звітували. */
    const Isr live = regs_.isr.load() & Isr::errors;
    if (any(live)) {
        clear(regs_, to_clear(live));
        bits |= raw(live);
    }

    return static_cast<Isr>(bits);
}

} // namespace usart
