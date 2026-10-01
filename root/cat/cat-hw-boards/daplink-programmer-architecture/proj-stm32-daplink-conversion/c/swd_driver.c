#include "swd_driver.h"

/**
 * @file swd_driver.c
 * @brief Реалізація обробників формування часових діаграм SWD для зчитування
 *        й запису регістрів цільових мікроконтролерів ARM Cortex-M.
 */

#define APB2PERIPH_BASE       0x40010000UL
#define GPIOB_BASE            (APB2PERIPH_BASE + 0x0C00UL)

#define GPIOB_CRH             (*(volatile uint32_t *)(GPIOB_BASE + 0x04UL))
#define GPIOB_IDR             (*(volatile uint32_t *)(GPIOB_BASE + 0x08UL))
#define GPIOB_BSRR            (*(volatile uint32_t *)(GPIOB_BASE + 0x10UL))
#define GPIOB_BRR             (*(volatile uint32_t *)(GPIOB_BASE + 0x14UL))

/* Біти керування пінами GPIOB: PB13 - SWCLK, PB14 - SWDIO, PB15 - RESET */
#define PIN_SWCLK             (1UL << 13)
#define PIN_SWDIO             (1UL << 14)
#define PIN_RESET             (1UL << 15)

/* Максимальна кількість спроб при отриманні SWD_ACK_WAIT */
#define SWD_RETRY_COUNT       1000U

static void swd_delay(void) {
    /* Невелика затримка для формування тактової частоти ~1-2 МГц */
    for (volatile int i = 0; i < 4; i++) {
        __asm__("nop");
    }
}

static uint8_t calculate_parity(uint32_t val) {
    uint32_t p = val ^ (val >> 16);
    p ^= p >> 8;
    p ^= p >> 4;
    p ^= p >> 2;
    p ^= p >> 1;
    return (uint8_t)(p & 0x01U);
}

void swd_init(void) {
    /* Початковий стан сигналів: SWCLK = Low, SWDIO = High, nRESET = High */
    GPIOB_BSRR = PIN_SWDIO | PIN_RESET;
    GPIOB_BRR  = PIN_SWCLK;
}

void swd_write_bit(uint8_t bit) {
    if (bit & 0x01U) {
        GPIOB_BSRR = PIN_SWDIO;
    } else {
        GPIOB_BRR  = PIN_SWDIO;
    }
    
    /* Спадущий та наростаючий фронти SWCLK */
    GPIOB_BRR = PIN_SWCLK;
    swd_delay();
    GPIOB_BSRR = PIN_SWCLK;
    swd_delay();
}

uint8_t swd_read_bit(void) {
    GPIOB_BRR = PIN_SWCLK;
    swd_delay();
    
    uint8_t bit = (GPIOB_IDR & PIN_SWDIO) ? 1U : 0U;
    
    GPIOB_BSRR = PIN_SWCLK;
    swd_delay();
    
    return bit;
}

void swd_turnaround(bool to_input) {
    if (to_input) {
        /* Налаштування PB14 (SWDIO) на Input Floating (CNF=01, MODE=00) */
        GPIOB_CRH &= ~(0xFUL << 24);
        GPIOB_CRH |=  (0x4UL << 24);
    } else {
        /* Налаштування PB14 (SWDIO) на Output Push-Pull 50MHz (CNF=00, MODE=11) */
        GPIOB_CRH &= ~(0xFUL << 24);
        GPIOB_CRH |=  (0x3UL << 24);
    }
    
    /* Один такт очікування Turnaround */
    GPIOB_BRR = PIN_SWCLK;
    swd_delay();
    GPIOB_BSRR = PIN_SWCLK;
    swd_delay();
}

void swd_line_reset(void) {
    swd_turnaround(false);
    
    /* Передача 56High бітів для повернення лінії у вихідний стан */
    for (int i = 0; i < 56; i++) {
        swd_write_bit(1);
    }
    
    /* Послідовність перемикання JTAG-to-SWD (0x79E7) */
    uint16_t switch_seq = 0x79E7U;
    for (int i = 0; i < 16; i++) {
        swd_write_bit((switch_seq >> i) & 1U);
    }
    
    /* Повторні 56 бітів High */
    for (int i = 0; i < 56; i++) {
        swd_write_bit(1);
    }
    
    /* 8 тактів очікування Idle (SWDIO = Low) */
    for (int i = 0; i < 8; i++) {
        swd_write_bit(0);
    }
}

uint8_t swd_transfer(uint8_t request, uint32_t *data) {
    uint8_t ack = 0;
    uint8_t parity = 0;

    /* Обчислення паритету для пакета запиту */
    uint8_t req_parity = calculate_parity(request & 0x1EU);

    swd_turnaround(false);
    
    /* 1. Передача Start Bit (1) */
    swd_write_bit(1);
    /* 2. APnDP */
    swd_write_bit((request >> 0) & 1U);
    /* 3. RnW */
    swd_write_bit((request >> 1) & 1U);
    /* 4. A[2:3] */
    swd_write_bit((request >> 2) & 1U);
    swd_write_bit((request >> 3) & 1U);
    /* 5. Parity */
    swd_write_bit(req_parity);
    /* 6. Stop Bit (0) */
    swd_write_bit(0);
    /* 7. Park Bit (1) */
    swd_write_bit(1);

    /* 8. Turnaround phase до приймання ACK */
    swd_turnaround(true);

    /* 9. Читання 3-бітного ACK */
    for (int i = 0; i < 3; i++) {
        ack |= (swd_read_bit() << i);
    }

    if (ack == SWD_ACK_OK) {
        if (request & SWD_REQ_READ) {
            /* Прийоми даних (32 біти) */
            uint32_t val = 0;
            for (int i = 0; i < 32; i++) {
                val |= ((uint32_t)swd_read_bit() << i);
            }
            /* Читання біта парності */
            parity = swd_read_bit();
            
            swd_turnaround(false);
            
            if (parity == calculate_parity(val)) {
                if (data) *data = val;
            } else {
                ack = SWD_ACK_PARITY;
            }
        } else {
            /* Запис даних у цільовий пристрій */
            swd_turnaround(false);
            
            uint32_t val = *data;
            for (int i = 0; i < 32; i++) {
                swd_write_bit((val >> i) & 1U);
            }
            /* Передача біта парності */
            swd_write_bit(calculate_parity(val));
        }
    } else {
        /* При помилці завершуємо такт очікування */
        swd_turnaround(false);
    }

    /* Idle clocks (8 тактів) */
    for (int i = 0; i < 8; i++) {
        swd_write_bit(0);
    }

    return ack;
}

bool swd_read_dp(uint8_t reg_addr, uint32_t *val) {
    uint8_t request = SWD_REQ_DP | SWD_REQ_READ | ((reg_addr & 0x0CU));
    for (uint32_t retry = 0; retry < SWD_RETRY_COUNT; retry++) {
        uint8_t ack = swd_transfer(request, val);
        if (ack == SWD_ACK_OK) return true;
        if (ack != SWD_ACK_WAIT) break;
    }
    return false;
}

bool swd_write_dp(uint8_t reg_addr, uint32_t val) {
    uint8_t request = SWD_REQ_DP | SWD_REQ_WRITE | ((reg_addr & 0x0CU));
    for (uint32_t retry = 0; retry < SWD_RETRY_COUNT; retry++) {
        uint8_t ack = swd_transfer(request, &val);
        if (ack == SWD_ACK_OK) return true;
        if (ack != SWD_ACK_WAIT) break;
    }
    return false;
}

bool swd_read_ap(uint32_t ap_addr, uint32_t *val) {
    uint32_t select_val = ap_addr & 0xFF0000F0UL;
    if (!swd_write_dp(DP_REG_SELECT, select_val)) return false;
    
    uint8_t request = SWD_REQ_AP | SWD_REQ_READ | ((ap_addr & 0x0CU));
    uint32_t dummy;
    /* Перше читання ініціює конвеєр AP */
    if (swd_transfer(request, &dummy) != SWD_ACK_OK) return false;
    /* Друге читання отримує реальний результат або читаємо з RDBUFF */
    return swd_read_dp(DP_REG_RDBUFF, val);
}

bool swd_write_ap(uint32_t ap_addr, uint32_t val) {
    uint32_t select_val = ap_addr & 0xFF0000F0UL;
    if (!swd_write_dp(DP_REG_SELECT, select_val)) return false;
    
    uint8_t request = SWD_REQ_AP | SWD_REQ_WRITE | ((ap_addr & 0x0CU));
    for (uint32_t retry = 0; retry < SWD_RETRY_COUNT; retry++) {
        uint8_t ack = swd_transfer(request, &val);
        if (ack == SWD_ACK_OK) return true;
        if (ack != SWD_ACK_WAIT) break;
    }
    return false;
}
