#include "usart_driver.h"

/* Найменший дільник при звичайному 16-кратному передискретизуванні:
 * менше — приймач не встигає набрати вибірок на біт. Стеля — розрядність
 * самого BRR. Обидва числа з Reference Manual, не з голови. */
#define BRR_MIN 16UL
#define BRR_MAX 0xFFFFUL

/* Верхня межа очікування, виражена в прохідках циклу.
 *
 * Це не годинник, а страховка від вічного зависання: точний час дала б
 * системна лічилка тактів, але на етапі підняття периферії її ще немає.
 * Рахуємо грубо й із запасом: символ — це 10 бітів плюс міжсимвольна
 * пауза, одна прохідка циклу коштує щонайменше кілька тактів ядра.
 */
static uint32_t spin_limit_for(uint32_t pclk_hz, uint32_t baud)
{
    const uint32_t cycles_per_bit = pclk_hz / baud;
    return cycles_per_bit * 12U + 64U;
}

/* Обхід апаратного дефекту Rev A з Errata Sheet.
 *
 * Дефект: якщо записати байт у TDR негайно після встановлення TE, перший
 * стартовий біт виходить некоректної тривалості. Документація вимагає
 * витримати щонайменше один такт периферійної шини.
 *
 * Зворотне читання регістра того самого блока — це повна транзакція
 * читання на APB. Вона не може початися раніше за попередній запис у той
 * самий блок і сама коштує не менше такту шини, тобто дає рівно те, чого
 * вимагає Errata. Порожній `nop` тут не годиться: ядро тактується швидше
 * за APB, і один такт ядра — це частка такту шини.
 */
static void te_settle(usart_regs_t *regs)
{
    (void)regs->CR1;
    usart_dsb();
}

/* Очікування прапорця в ISR із верхньою межею.
 * Читаємо ISR і нічого в нього не пишемо — це регістр стану. */
static usart_status_t wait_flag(usart_t *dev, uint32_t flag)
{
    uint32_t spin = dev->spin_limit;

    while ((dev->regs->ISR & flag) == 0U) {
        if (spin == 0U) {
            /* Передавач не звільнив буфер: обірваний такт периферії,
             * знятий тактовий сигнал, зупинений налагоджувачем блок. */
            return USART_ERR_TIMEOUT;
        }
        spin--;
    }
    return USART_OK;
}

/* Коротка критична секція для полів, які ділять головний цикл і обробник
 * переривання. Зберігаємо PRIMASK і відновлюємо його, а не вмикаємо
 * переривання наосліп: виклик міг статися вже під забороною. */
static uint32_t irq_lock(void)
{
    uint32_t primask;

    __asm__ volatile("mrs %0, primask" : "=r"(primask));
    __asm__ volatile("cpsid i" ::: "memory");
    return primask;
}

static void irq_unlock(uint32_t primask)
{
    if ((primask & 1U) == 0U) {
        __asm__ volatile("cpsie i" ::: "memory");
    }
}

/* Прапорці помилок у ISR і біти їх гасіння в ICR стоять на однакових
 * позиціях, але це збіг конкретного блока, а не закон. Перекладаємо
 * явно — тоді карта наступного чипа не зламає код мовчки. */
static uint32_t isr_errors_to_icr(uint32_t isr)
{
    uint32_t icr = 0U;

    if (isr & USART_ISR_PE)  { icr |= USART_ICR_PECF;  }
    if (isr & USART_ISR_FE)  { icr |= USART_ICR_FECF;  }
    if (isr & USART_ISR_NF)  { icr |= USART_ICR_NCF;   }
    if (isr & USART_ISR_ORE) { icr |= USART_ICR_ORECF; }
    return icr;
}

usart_status_t usart_init_tx(usart_t *dev, usart_regs_t *regs,
                             uint32_t pclk_hz, uint32_t baud)
{
    if (baud == 0U || pclk_hz == 0U) {
        return USART_ERR_BAUD;
    }

    /* Дільник із округленням до найближчого: відкидання дробової частини
     * дає похибку швидкості, і на довгому кадрі приймач з'їжджає з біта. */
    const uint32_t brr = (pclk_hz + baud / 2U) / baud;
    if (brr < BRR_MIN || brr > BRR_MAX) {
        /* Або шина занадто повільна для цієї швидкості, або занадто
         * швидка: у BRR таке число не влазить, і мовчки писати обрізане
         * значення означає віддати в лінію сміття. */
        return USART_ERR_BAUD;
    }

    /* Ревізію питаємо тут і зберігати її нема потреби: TE піднімається
     * рівно один раз, і дефект стосується тільки цієї миті. */
    const bool te_workaround = silicon_needs_te_workaround(silicon_revision());

    dev->regs          = regs;
    dev->spin_limit    = spin_limit_for(pclk_hz, baud);
    dev->sticky_errors = 0U;

    /* Порядок важливий: швидкість налаштовуємо, поки блок вимкнений.
     * Запис у BRR при піднятому UE документація лишає невизначеним. */
    regs->CR1 = 0U;
    regs->BRR = brr;

    /* Повний запис, а не |=: після скидання решта бітів CR1 нульова, і
     * read-modify-write тут лише додав би вікно для гонки без користі. */
    regs->CR1 = USART_CR1_UE | USART_CR1_TE;

    if (te_workaround) {
        te_settle(regs);
    }

    /* Прапорці, що лишилися від попереднього сеансу (або від сміття на
     * лінії, поки блок піднімався), гасимо до першої відправки. */
    usart_clear_flags(regs, USART_ICR_ERRORS | USART_ICR_TCCF);

    return USART_OK;
}

void usart_enable_rx_irq(usart_t *dev)
{
    /* Тут read-modify-write доречний і безпечний: CR1 — регістр керування,
     * апаратура сама в нього не пише, конкурента в цій гонці немає. */
    dev->regs->CR1 |= USART_CR1_RXNEIE;
}

usart_status_t usart_send_byte(usart_t *dev, uint8_t byte)
{
    const usart_status_t st = wait_flag(dev, USART_ISR_TXE);
    if (st != USART_OK) {
        return st;
    }

    /* Один 32-бітний запис у TDR. Старші біти апаратура відкидає сама,
     * але маскуємо явно — щоб у коді було видно ширину слова даних. */
    dev->regs->TDR = (uint32_t)byte & USART_TDR_MASK;
    return USART_OK;
}

usart_status_t usart_send(usart_t *dev, const uint8_t *data, size_t len,
                          size_t *sent)
{
    size_t done = 0U;
    usart_status_t st = USART_OK;

    for (; done < len; done++) {
        st = usart_send_byte(dev, data[done]);
        if (st != USART_OK) {
            break;
        }
    }

    if (sent != NULL) {
        *sent = done;
    }
    return st;
}

usart_status_t usart_flush(usart_t *dev)
{
    const usart_status_t st = wait_flag(dev, USART_ISR_TC);
    if (st != USART_OK) {
        return st;
    }

    /* TC гасимо записом одиниці в TCCF регістра ICR. Класичне
     * ISR &= ~TC зняло б заразом і RXNE, який апаратура могла підняти
     * між нашим читанням і зворотним записом. */
    usart_clear_flags(dev->regs, USART_ICR_TCCF);
    return USART_OK;
}

uint32_t usart_take_errors(usart_t *dev)
{
    /* Помилку може зняти або обробник переривання, або цей виклик — хто
     * перший побачив. Тому забираємо відкладене й живе разом, під однією
     * забороною переривань: інакше помилка, знята обробником одразу після
     * нашого читання ISR, лишилася б у sticky_errors до наступного кола. */
    const uint32_t key = irq_lock();

    uint32_t errors = dev->sticky_errors;
    dev->sticky_errors = 0U;

    /* Одне читання ISR: два підряд дали б два різні знімки стану, і
     * погасити ми могли б не те, про що звітували. */
    const uint32_t live = dev->regs->ISR & USART_ISR_ERRORS;
    if (live != 0U) {
        usart_clear_flags(dev->regs, isr_errors_to_icr(live));
        errors |= live;
    }

    irq_unlock(key);
    return errors;
}

void usart_irq_handler(usart_t *dev, void (*sink)(uint8_t byte))
{
    /* Знімок стану робиться один раз на вхід у обробник. Далі всі
     * рішення ухвалюються за цим знімком, а не за живим регістром:
     * інакше два звернення до ISR у сусідніх рядках побачать різне. */
    const uint32_t isr = dev->regs->ISR;
    uint32_t to_clear = 0U;

    if (isr & USART_ISR_ERRORS) {
        /* Гасимо тут-таки — інакше ORE тримає переривання піднятим і
         * обробник крутиться без кінця, — а сам факт відкладаємо: доповідь
         * про помилку сама займає лінію, і робити це з переривання не можна. */
        to_clear |= isr_errors_to_icr(isr);
        dev->sticky_errors |= isr & USART_ISR_ERRORS;
    }

    if (isr & USART_ISR_RXNE) {
        /* Читання RDR скидає RXNE апаратно — саме тому в ICR немає біта
         * для нього. Байт треба забрати навіть без споживача, інакше
         * наступний символ дасть переповнення ORE. */
        const uint8_t byte = (uint8_t)(dev->regs->RDR & 0xFFU);
        if (sink != NULL) {
            sink(byte);
        }
    }

    if (isr & USART_ISR_TC) {
        to_clear |= USART_ICR_TCCF;
    }

    if (to_clear != 0U) {
        /* Один запис у ICR на всі прапорці разом і бар'єр усередині
         * usart_clear_flags. Без бар'єра ядро вийде з обробника раніше,
         * ніж скидання добіжить шиною, і NVIC викличе нас удруге на тій
         * самій події. */
        usart_clear_flags(dev->regs, to_clear);
    } else {
        /* Переривання без жодного відомого нам прапорця: бар'єр однаково
         * потрібен, бо RDR ми могли читати, а буфер запису спільний. */
        usart_dsb();
    }
}
