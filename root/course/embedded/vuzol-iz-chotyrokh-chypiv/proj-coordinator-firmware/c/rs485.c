#include <string.h>

#include "stm32l4xx.h"
#include "node.h"
#include "rs485.h"

#define RX_BUF_SIZE 64u
#define TX_BUF_SIZE 40u
#define DE_PIN      8u        /* PA8 */

#define FUNC_READ_HOLDING 0x03u
#define EXC_ILLEGAL_FUNC  0x01u

static volatile uint8_t  rx_buf[RX_BUF_SIZE];
static volatile uint16_t rx_len;
static volatile uint8_t  frame_buf[RX_BUF_SIZE];
static volatile uint16_t frame_len;
static volatile bool     frame_ready;
static volatile uint32_t rx_overruns;

static volatile uint8_t  tx_buf[TX_BUF_SIZE];
static volatile uint16_t tx_len;
static volatile uint16_t tx_pos;
static volatile bool     tx_busy;

static volatile uint32_t last_poll_ms;
static volatile bool     master_seen;

static void de_high(void) { GPIOA->BSRR = (1u << DE_PIN); }
static void de_low(void)  { GPIOA->BSRR = (1u << (DE_PIN + 16u)); }

void rs485_init(uint32_t kernel_clk_hz)
{
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_USART1EN;

    /* Ядро USART тактуємо від HSI16: тоді приймач живий і в режимі Stop 2,
     * і перший же старт-біт від ведучого будить мікроконтролер. */
    RCC->CCIPR = (RCC->CCIPR & ~RCC_CCIPR_USART1SEL) | (2u << RCC_CCIPR_USART1SEL_Pos);
    RCC->CR |= RCC_CR_HSION | RCC_CR_HSIASFS;      /* HSI16 сам стартує після Stop */
    while ((RCC->CR & RCC_CR_HSIRDY) == 0u) { }

    /* PA9/PA10 → AF7 (USART1), PA8 → вихід DE, спокійний стан — прийом. */
    GPIOA->AFR[1] = (GPIOA->AFR[1] & ~0x00000FF0u) | 0x00000770u;
    GPIOA->MODER  = (GPIOA->MODER & ~0x003F0000u) | 0x00290000u;  /* PA8 вих., PA9/10 AF */
    de_low();

    USART1->CR1 = 0;
    USART1->BRR = kernel_clk_hz / RS485_BAUD;      /* 16 МГц / 19200 = 833 */

    /* t3.5 між символами: 3.5 × 11 бітів ≈ 39 бітових інтервалів. Детектор
     * Receiver Timeout відміряє їх апаратно — програмному таймеру тут не
     * встигнути, а саме ця пауза й означає «кадр скінчився». */
    USART1->RTOR = 39u;
    USART1->CR2 = USART_CR2_RTOEN;
    USART1->CR3 = USART_CR3_WUFIE | (3u << USART_CR3_WUS_Pos);   /* прокидання по RXNE */
    USART1->CR1 = USART_CR1_UE | USART_CR1_UESM | USART_CR1_TE | USART_CR1_RE |
                  USART_CR1_RXNEIE | USART_CR1_RTOIE;

    NVIC_SetPriority(USART1_IRQn, 2u);
    NVIC_EnableIRQ(USART1_IRQn);
}

/* ── Переривання каналу ──────────────────────────────────────────────────── */

void USART1_IRQHandler(void)
{
    uint32_t isr = USART1->ISR;

    if (isr & USART_ISR_WUF) {
        USART1->ICR = USART_ICR_WUCF;              /* прокинулися від старт-біта */
    }

    if (isr & (USART_ISR_ORE | USART_ISR_FE | USART_ISR_NE)) {
        USART1->ICR = USART_ICR_ORECF | USART_ICR_FECF | USART_ICR_NCF;
        rx_overruns++;
        rx_len = 0;                                 /* кадр однаково битий */
    }

    if (isr & USART_ISR_RXNE) {
        uint8_t byte = (uint8_t)USART1->RDR;

        if (!frame_ready && rx_len < RX_BUF_SIZE) {
            rx_buf[rx_len++] = byte;
        } else if (rx_len >= RX_BUF_SIZE) {
            rx_len = 0;                             /* довший за наш буфер — не наш */
        }
    }

    if (isr & USART_ISR_RTOF) {
        USART1->ICR = USART_ICR_RTOCF;

        if (rx_len > 0u && !frame_ready) {
            memcpy((void *)frame_buf, (const void *)rx_buf, rx_len);
            frame_len = rx_len;
            frame_ready = true;
            events_push(NODE_EVENT_RS485_FRAME);
        }
        rx_len = 0;
    }

    /* Передавання: байти віддаємо по TXE, а лінію DE знімаємо лише по TC. */
    if ((USART1->CR1 & USART_CR1_TXEIE) && (isr & USART_ISR_TXE)) {
        if (tx_pos < tx_len) {
            USART1->TDR = tx_buf[tx_pos++];
        } else {
            USART1->CR1 &= ~USART_CR1_TXEIE;
            USART1->ICR = USART_ICR_TCCF;
            USART1->CR1 |= USART_CR1_TCIE;
        }
    }

    if ((USART1->CR1 & USART_CR1_TCIE) && (isr & USART_ISR_TC)) {
        USART1->ICR = USART_ICR_TCCF;
        USART1->CR1 &= ~USART_CR1_TCIE;
        /* TXE каже лише «регістр звільнився»: зняти DE тут — обрізати
         * останній байт просто в лінії. Чекаємо саме TC. */
        de_low();
        tx_busy = false;
        events_push(NODE_EVENT_RS485_SENT);
    }
}

/* ── Передавання відповіді ───────────────────────────────────────────────── */

static void rs485_send(const uint8_t *data, uint16_t len)
{
    if (len == 0u || len > TX_BUF_SIZE || tx_busy) return;

    memcpy((void *)tx_buf, data, len);
    tx_len = len;
    tx_pos = 0;
    tx_busy = true;

    de_high();
    /* Трансиверу треба одиниці мікросекунд на перехід у передавання;
     * поки він переходить, перший байт уже в дорозі — тому пауза потрібна. */
    delay_us(2);

    USART1->ICR = USART_ICR_TCCF;
    USART1->CR1 |= USART_CR1_TXEIE;
}

/* ── Розбір запиту ───────────────────────────────────────────────────────── */

void rs485_service(const telemetry_record_t *last)
{
    uint8_t  req[RX_BUF_SIZE];
    uint16_t len;

    if (!frame_ready) return;

    __disable_irq();
    len = frame_len;
    memcpy(req, (const void *)frame_buf, len);
    frame_ready = false;
    __enable_irq();

    if (len < 4u) return;                          /* коротше за адресу+код+CRC */
    if (req[0] != RS485_NODE_ID) return;           /* кадр не наш — мовчимо */

    uint16_t rx_crc = (uint16_t)req[len - 2] | ((uint16_t)req[len - 1] << 8);
    if (crc16_modbus(req, (uint16_t)(len - 2u)) != rx_crc) {
        return;                                    /* биту суму лишаємо без відповіді */
    }

    last_poll_ms = millis();
    master_seen = true;

    uint8_t  resp[TX_BUF_SIZE];
    uint16_t n = 0;

    if (req[1] == FUNC_READ_HOLDING) {
        resp[n++] = RS485_NODE_ID;
        resp[n++] = FUNC_READ_HOLDING;
        resp[n++] = (uint8_t)sizeof(telemetry_record_t);
        memcpy(&resp[n], last, sizeof(telemetry_record_t));
        n += (uint16_t)sizeof(telemetry_record_t);
    } else {
        /* Виняткова відповідь: ведучий має знати, що вузол живий, але
         * такої функції не має. Мовчання він прочитав би як обрив. */
        resp[n++] = RS485_NODE_ID;
        resp[n++] = (uint8_t)(req[1] | 0x80u);
        resp[n++] = EXC_ILLEGAL_FUNC;
    }

    uint16_t crc = crc16_modbus(resp, n);
    resp[n++] = (uint8_t)(crc & 0xFFu);
    resp[n++] = (uint8_t)(crc >> 8);

    rs485_send(resp, n);
}

bool rs485_tx_busy(void)
{
    return tx_busy;
}

bool rs485_frame_waiting(void)
{
    return frame_ready;
}

uint32_t rs485_last_poll_ms(void)
{
    return last_poll_ms;
}

bool rs485_master_active(void)
{
    return master_seen && ((millis() - last_poll_ms) < RS485_ACTIVE_WINDOW_MS);
}
