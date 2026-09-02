#include "i2c_recovery.h"

#include "delay.h"
#include "stm32f10x.h"

/* Штатна розкладка I2C1 на STM32F103: PB6 = SCL, PB7 = SDA */
#define SCL_MASK          (1U << 6)
#define SDA_MASK          (1U << 7)

/* Нібли CRL для виводів 6 і 7: CNF+MODE одним значенням */
#define MODE_GPIO_OD      0x7U   /* звичайний вихід Open-Drain, 10 МГц */
#define MODE_AF_OD        0xBU   /* той самий вихід, але веде його периферія */

/* Напівперіод ручного тактування. Стандартний режим вимагає щонайменше
   4.7 мкс утримання рівня; коротший імпульс вхідний фільтр веденого чипа має
   повне право прийняти за голку й проковтнути — тоді байт не зсунеться. */
#define HALF_PERIOD_US    5U

/* Запас на пологий фронт: 10 кОм підтяжки на 200 пФ ємності шини дають
   постійну часу близько 2 мкс, і рівень 1 з'являється помітно пізніше за
   команду «відпустити». Плюс тут же ловиться розтягування такту веденим. */
#define RISE_TIMEOUT_US   100U

#define CLOCK_PULSES      9U

static void pins_set_mode(uint32_t nibble) {
    uint32_t crl = GPIOB->CRL;
    crl &= ~0xFF000000U;                              /* нібли виводів 6 і 7 */
    crl |= (nibble << 24) | (nibble << 28);
    GPIOB->CRL = crl;
}

/* Старші 16 бітів BSRR притискають вивід, молодші — відпускають */
static void line_pull_low(uint32_t mask) {
    GPIOB->BSRR = mask << 16;
}

static void line_release(uint32_t mask) {
    GPIOB->BSRR = mask;
}

static int line_is_high(uint32_t mask) {
    return (GPIOB->IDR & mask) != 0U;
}

static int wait_line_high(uint32_t mask, uint32_t timeout_us) {
    uint32_t waited;
    for (waited = 0U; waited <= timeout_us; ++waited) {
        if (line_is_high(mask)) {
            return 1;
        }
        delay_us(1U);
    }
    return 0;
}

i2c_bus_report_t i2c1_bus_recover(void) {
    i2c_bus_report_t report;
    report.status = I2C_BUS_OK;
    report.pulses = 0U;

    /* 1. Тактування порту й AFIO: без нього запис у CRL просто нікуди не піде */
    RCC->APB2ENR |= RCC_APB2ENR_IOPBEN | RCC_APB2ENR_AFIOEN;
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    /* 2. Модуль тримаємо у скиданні протягом УСЬОГО ручного тактування. Це і
       чистить залиплий скінченний автомат з аналоговим фільтром, і не дає
       контролеру побачити чужі фронти на власних виводах і знову впасти в BERR. */
    RCC->APB1RSTR |= RCC_APB1RSTR_I2C1RST;
    delay_us(2U);

    /* 3. Забираємо виводи собі й відпускаємо обидві лінії */
    pins_set_mode(MODE_GPIO_OD);
    line_release(SCL_MASK);
    line_release(SDA_MASK);

    if (!wait_line_high(SCL_MASK, RISE_TIMEOUT_US)) {
        /* Такт не піднявся навіть без нашого втручання — тактувати нічим */
        report.status = I2C_BUS_SCL_STUCK;
        return report;
    }
    delay_us(HALF_PERIOD_US);

    /* 4. До дев'яти тактів, доки ведений не догортає свій байт і не відпустить
       SDA. Прапорець перевіряємо ПЕРЕД кожним тактом: якщо чип звільнив лінію
       на третьому, решту шести видавати немає потреби. */
    while (!line_is_high(SDA_MASK) && report.pulses < CLOCK_PULSES) {
        line_pull_low(SCL_MASK);
        delay_us(HALF_PERIOD_US);

        line_release(SCL_MASK);
        if (!wait_line_high(SCL_MASK, RISE_TIMEOUT_US)) {
            report.status = I2C_BUS_SCL_STUCK;
            return report;
        }
        delay_us(HALF_PERIOD_US);

        report.pulses++;
    }

    if (!line_is_high(SDA_MASK)) {
        /* Дев'ять тактів зсувають будь-який байт до кінця. Якщо дані досі внизу,
           це вже не протокол: коротке замикання на платі або мертвий кристал. */
        report.status = I2C_BUS_SDA_STUCK;
        return report;
    }

    /* 5. Ручний STOP: при високому SCL переводимо SDA з нуля в одиницю. Усі
       ведені на шині сприймуть це як кінець транзакції й підуть чекати адреси. */
    line_pull_low(SDA_MASK);
    delay_us(HALF_PERIOD_US);
    line_release(SCL_MASK);          /* SCL і так високий — тримаємо його таким */
    delay_us(HALF_PERIOD_US);
    line_release(SDA_MASK);
    if (!wait_line_high(SDA_MASK, RISE_TIMEOUT_US)) {
        report.status = I2C_BUS_SDA_STUCK;
        return report;
    }
    delay_us(HALF_PERIOD_US);

    /* 6. Обидві лінії у спокої — віддаємо виводи периферії й знімаємо скидання */
    if (!line_is_high(SCL_MASK)) {
        report.status = I2C_BUS_SCL_STUCK;
        return report;
    }
    pins_set_mode(MODE_AF_OD);
    RCC->APB1RSTR &= ~RCC_APB1RSTR_I2C1RST;

    return report;
}
