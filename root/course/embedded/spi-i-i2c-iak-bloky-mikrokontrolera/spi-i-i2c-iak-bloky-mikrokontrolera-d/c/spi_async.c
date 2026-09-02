#include "spi_async.h"

/* Прапорці потоків DMA2 у регістрі LISR/LIFCR: група потоку 2 починається
   з біта 16, потоку 3 — з біта 22; усередині групи TC = +5, TE = +3. */
#define DMA_S2_ALL   (0x3FU << 16)
#define DMA_S2_TCIF  (1U << 21)
#define DMA_S2_TEIF  (1U << 19)
#define DMA_S3_ALL   (0x3FU << 22)
#define DMA_S3_TCIF  (1U << 27)
#define DMA_S3_TEIF  (1U << 25)

typedef struct {
    const uint8_t *tx;
    uint8_t *rx;
    size_t len;
    size_t sent;
    size_t received;
    spi_done_cb_t cb;
    volatile bool busy;
} xfer_t;

static xfer_t g_xfer;

/* Куди DMA зливає непотрібні прийняті байти й звідки бере заповнювач,
   коли передавати нічого. Інкремент адреси для них вимкнено. */
static uint8_t g_sink;
static const uint8_t g_filler = 0xFFU;

void spi1_async_init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_DMA2EN;
    nvic_enable_irq(IRQ_SPI1);
    nvic_enable_irq(IRQ_DMA2_STREAM2);
}

bool spi1_async_busy(void)
{
    return g_xfer.busy;
}

static void finish(spi_status_t status)
{
    SPI1->CR2 &= ~(SPI_CR2_RXNEIE | SPI_CR2_ERRIE | SPI_CR2_TXEIE |
                   SPI_CR2_TXDMAEN | SPI_CR2_RXDMAEN);
    spi1_cs_release();
    g_xfer.busy = false;
    if (g_xfer.cb != NULL) {
        g_xfer.cb(status);
    }
}

static uint8_t next_tx_byte(void)
{
    uint8_t b = (g_xfer.tx != NULL) ? g_xfer.tx[g_xfer.sent] : 0xFFU;
    g_xfer.sent++;
    return b;
}

spi_status_t spi1_irq_start(const uint8_t *tx, uint8_t *rx, size_t len, spi_done_cb_t cb)
{
    if (len == 0U) {
        return SPI_ERR_ARG;
    }
    if (g_xfer.busy) {
        return SPI_ERR_BUSY;
    }

    g_xfer.tx = tx;
    g_xfer.rx = rx;
    g_xfer.len = len;
    g_xfer.sent = 0U;
    g_xfer.received = 0U;
    g_xfer.cb = cb;
    g_xfer.busy = true;

    spi1_cs_select();

    /* TXEIE НЕ вмикаємо навмисно: буфер передачі порожній майже завжди,
       і дозволене TXE дало б безкінечний шторм переривань. Наступний байт
       кладемо в DR у відповідь на RXNE — так у польоті рівно одне слово
       і переповнення OVR не виникає в принципі. */
    SPI1->CR2 |= SPI_CR2_RXNEIE | SPI_CR2_ERRIE;
    SPI1->DR = next_tx_byte();
    return SPI_OK;
}

void SPI1_IRQHandler(void)
{
    uint32_t sr = SPI1->SR;

    if (sr & SPI_SR_MODF) {
        spi_recover_mode_fault(SPI1);
        finish(SPI_ERR_MODE_FAULT);
        return;
    }
    if (sr & SPI_SR_OVR) {
        spi_clear_overrun(SPI1);
        finish(SPI_ERR_OVERRUN);
        return;
    }
    if (!(sr & SPI_SR_RXNE)) {
        return;
    }

    uint8_t received = (uint8_t)(SPI1->DR & 0xFFU);
    if (g_xfer.rx != NULL) {
        g_xfer.rx[g_xfer.received] = received;
    }
    g_xfer.received++;

    if (g_xfer.received == g_xfer.len) {
        finish(SPI_OK);
        return;
    }
    SPI1->DR = next_tx_byte();
}

static void dma_stream_setup(dma_stream_t *s, uint32_t mem, uint32_t flags, size_t len)
{
    s->CR = 0U;
    while (s->CR & DMA_CR_EN) {
        /* потік вимикається не миттєво: чекаємо, поки апаратура відпустить EN */
    }
    s->PAR = (uint32_t)(uintptr_t)&SPI1->DR;
    s->M0AR = mem;
    s->NDTR = (uint32_t)len;
    s->CR = flags | (3U << DMA_CR_CHSEL_POS) | DMA_CR_PL_HIGH;
}

spi_status_t spi1_dma_start(const uint8_t *tx, uint8_t *rx, size_t len, spi_done_cb_t cb)
{
    if (len == 0U) {
        return SPI_ERR_ARG;
    }
    if (g_xfer.busy) {
        return SPI_ERR_BUSY;
    }

    g_xfer.tx = tx;
    g_xfer.rx = rx;
    g_xfer.len = len;
    g_xfer.cb = cb;
    g_xfer.busy = true;

    DMA2->LIFCR = DMA_S2_ALL | DMA_S3_ALL;   /* старі прапорці завершення геть */

    /* Приймальний потік: периферія -> пам'ять. Коли відповідь не потрібна,
       усі байти зливаються в один байт-смітник із вимкненим інкрементом. */
    uint32_t rx_flags = DMA_CR_TCIE | DMA_CR_TEIE;
    if (rx != NULL) {
        rx_flags |= DMA_CR_MINC;
    }
    dma_stream_setup(&DMA2->S[2], (uint32_t)(uintptr_t)((rx != NULL) ? rx : &g_sink),
                     rx_flags, len);

    /* Передавальний потік: пам'ять -> периферія */
    uint32_t tx_flags = DMA_CR_DIR_M2P | DMA_CR_TEIE;
    if (tx != NULL) {
        tx_flags |= DMA_CR_MINC;
    }
    dma_stream_setup(&DMA2->S[3], (uint32_t)(uintptr_t)((tx != NULL) ? tx : &g_filler),
                     tx_flags, len);

    spi1_cs_select();

    /* Приймач вмикаємо ПЕРШИМ: якби першим пішов передавач, перший же
       прийнятий байт не мав би кому дістатися і дав би OVR. */
    DMA2->S[2].CR |= DMA_CR_EN;
    DMA2->S[3].CR |= DMA_CR_EN;
    SPI1->CR2 |= SPI_CR2_RXDMAEN | SPI_CR2_TXDMAEN;
    return SPI_OK;
}

void DMA2_Stream2_IRQHandler(void)
{
    uint32_t isr = DMA2->LISR;

    if (isr & DMA_S2_TEIF) {
        DMA2->LIFCR = DMA_S2_ALL | DMA_S3_ALL;
        DMA2->S[2].CR = 0U;
        DMA2->S[3].CR = 0U;
        finish(SPI_ERR_OVERRUN);   /* збій доступу до пам'яті — дані втрачено */
        return;
    }
    if (!(isr & DMA_S2_TCIF)) {
        return;
    }

    /* Приймальний потік завершується ОСТАННІМ: якщо він порахував усі
       слова, обмін справді закінчено. Лишається дочекатися, поки згасне
       BSY — кілька тактів SCK, які вже в дорозі. */
    DMA2->LIFCR = DMA_S2_ALL | DMA_S3_ALL;
    DMA2->S[2].CR = 0U;
    DMA2->S[3].CR = 0U;
    (void)spi_wait_idle(SPI1, SPI_POLL_BUDGET);
    finish(SPI_OK);
}
