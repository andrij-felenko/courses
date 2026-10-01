#include "daplink_board.h"
#include <string.h>

// Опис транзакції шини SWD
typedef struct {
    uint8_t request;    // Байт запиту (APnDP, RnW, Addr[2:3], Parity, Stop, Start)
    uint8_t ack;        // Статус відповіді (1=OK, 2=WAIT, 4=FAULT)
    uint32_t data;      // 32-бітове значення даних
    uint8_t parity;     // Біт парності
} SWD_Transaction_t;

// Формування програмної затримки для налаштування частоти SWCLK
static void swd_delay(void) {
    volatile uint32_t cycles = g_dap_port_config.clock_speed_hz < 1000000U ? 10U : 2U;
    while (cycles--) {
        __asm__("nop");
    }
}

// Генерація одного тактового імпульсу SWCLK із записом біта даних
static void swd_write_bit(uint8_t bit) {
    if (bit & 0x01U) {
        SWDIO_HIGH();
    } else {
        SWDIO_LOW();
    }
    swd_delay();
    SWCLK_HIGH();
    swd_delay();
    SWCLK_LOW();
}

// Зчитування одного біта з лінії SWDIO на наростаючому фронті SWCLK
static uint8_t swd_read_bit(void) {
    uint8_t bit;
    swd_delay();
    SWCLK_HIGH();
    bit = SWDIO_READ();
    swd_delay();
    SWCLK_LOW();
    return bit;
}

// Передача серії тактових імпульсів з утриманням фіксованого значення SWDIO
static void swd_clock_cycles(uint32_t count, uint8_t level) {
    if (level) {
        SWDIO_HIGH();
    } else {
        SWDIO_LOW();
    }
    for (uint32_t i = 0; i < count; i++) {
        swd_delay();
        SWCLK_HIGH();
        swd_delay();
        SWCLK_LOW();
    }
}

// Генерація сигнальної послідовності скидання шини SWD та переключення з JTAG (50+ імпульсів)
void swd_line_reset(void) {
    gpio_set_swdio_mode(SWDIO_MODE_OUTPUT_PP);
    // 50+ імпульсів із високим рівнем SWDIO
    swd_clock_cycles(56, 1);
    
    // 16-бітова послідовність перемикання JTAG-to-SWD (0xE79E в LSB першим)
    uint16_t switch_code = 0xE79EU;
    for (int i = 0; i < 16; i++) {
        swd_write_bit((switch_code >> i) & 0x01U);
    }
    
    // Повторні 50+ імпульсів та 8 фазових імпульсів затримки Trn
    swd_clock_cycles(56, 1);
    swd_clock_cycles(8, 0);
}

// Виконання однієї транзакції SWD (запит, перемикання Trn, зчитування ACK, обмін даними)
bool swd_transact(SWD_Transaction_t *trans) {
    gpio_set_swdio_mode(SWDIO_MODE_OUTPUT_PP);

    // 1. Передача 8-бітового байта запиту
    for (int i = 0; i < 8; i++) {
        swd_write_bit((trans->request >> i) & 0x01U);
    }

    // 2. Фаза Turnaround (Trn): перемикаємо SWDIO на вхід
    gpio_set_swdio_mode(SWDIO_MODE_INPUT_PULLUP);
    swd_read_bit(); // 1 тактовий імпульс Trn

    // 3. Зчитування 3-бітового статусу ACK (LSB first)
    trans->ack = 0;
    for (int i = 0; i < 3; i++) {
        trans->ack |= (swd_read_bit() << i);
    }

    if (trans->ack != 1U) { // 1 = ACK OK
        // Фаза Trn назад і вихід при помилці ACK
        swd_clock_cycles(1, 0);
        return false;
    }

    // 4. Передача або зчитування 32 бітів даних
    if (trans->request & (1U << 2)) { // Read operation (RnW = 1)
        trans->data = 0;
        for (int i = 0; i < 32; i++) {
            trans->data |= ((uint32_t)swd_read_bit() << i);
        }
        trans->parity = swd_read_bit();
        // Trn назад на вихід
        gpio_set_swdio_mode(SWDIO_MODE_OUTPUT_PP);
    } else { // Write operation (RnW = 0)
        // Trn назад на вихід
        gpio_set_swdio_mode(SWDIO_MODE_OUTPUT_PP);
        swd_read_bit(); // Trn
        for (int i = 0; i < 32; i++) {
            swd_write_bit((trans->data >> i) & 0x01U);
        }
        swd_write_bit(trans->parity);
    }

    // Фазові такти розвантаження шини
    swd_clock_cycles(2, 0);
    return true;
}
