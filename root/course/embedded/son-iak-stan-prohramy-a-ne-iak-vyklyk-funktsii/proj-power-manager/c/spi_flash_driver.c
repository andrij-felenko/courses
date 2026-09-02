/* spi_flash_driver.c — SPI1 + DMA1_Channel3, PA4 CS, PA5 SCK, PA6 MISO, PA7 MOSI.
 * Мікросхема сімейства W25Q/AT25: сторінка 256 байтів, Deep Power-Down 0xB9. */
#include "spi_flash_driver.h"
#include "power_manager.h"
#include "stm32l4xx.h"

#define CMD_WREN 0x06u
#define CMD_PP   0x02u
#define CMD_RDSR 0x05u
#define CMD_DPD  0xB9u
#define CMD_RES  0xABu
#define SR_WIP   0x01u

#define CS_PIN    4u
#define SPI_SPINS 100000u
/* tRES1 — вихід із Deep Power-Down триває до 3 мкс; на 80 МГц це ~240 тактів. */
#define RES_SPINS 300u

typedef enum {
    ST_IDLE = 0,   /* мікросхема вільна, сон дозволено */
    ST_DMA,        /* дані течуть у SPI через DMA */
    ST_PROGRAM     /* байти віддані, мікросхема пече сторінку сама */
} flash_state_t;

static volatile flash_state_t s_state;
static volatile bool s_locked;      /* чи тримаємо PM_LOCK_NO_STOP */
static volatile uint32_t s_errors;
static bool     s_deep_power_down;
static uint32_t s_saved_moder;

static void cs_low(void)  { GPIOA->BSRR = (1u << (CS_PIN + 16u)); }
static void cs_high(void) { GPIOA->BSRR = (1u << CS_PIN); }

static void release_lock(void)
{
    if (s_locked) {
        s_locked = false;
        pm_lock_release(PM_LOCK_NO_STOP);
    }
}

/* Один байт туди-сюди. Мертва шина не має зависати назавжди:
 * повертаємо false і рахуємо помилку. */
static bool spi_xfer(uint8_t out, uint8_t *in)
{
    uint32_t spins = SPI_SPINS;
    while ((SPI1->SR & SPI_SR_TXE) == 0u) {
        if (spins-- == 0u) { s_errors++; return false; }
    }
    *(volatile uint8_t *)&SPI1->DR = out;

    spins = SPI_SPINS;
    while ((SPI1->SR & SPI_SR_RXNE) == 0u) {
        if (spins-- == 0u) { s_errors++; return false; }
    }
    uint8_t got = *(volatile uint8_t *)&SPI1->DR;
    if (in) {
        *in = got;
    }
    return true;
}

/* Після передачі через DMA приймальний FIFO лишається повним — його треба
 * вичерпати, інакше наступний spi_xfer прочитає старе сміття. */
static void spi_drain_rx(void)
{
    uint32_t spins = SPI_SPINS;
    while ((SPI1->SR & SPI_SR_FRLVL) != 0u && spins-- != 0u) {
        (void)*(volatile uint8_t *)&SPI1->DR;
    }
}

static void spi_pins_active(void)
{
    /* PA5/PA6/PA7 — альтернативна функція AF5 (SPI1), PA4 — звичайний вихід */
    GPIOA->MODER = (GPIOA->MODER & ~(0xFFu << (CS_PIN * 2u)))
                 | (0x01u << (4u * 2u))   /* PA4 output */
                 | (0x02u << (5u * 2u))   /* PA5 AF */
                 | (0x02u << (6u * 2u))   /* PA6 AF */
                 | (0x02u << (7u * 2u));  /* PA7 AF */
    GPIOA->AFR[0] = (GPIOA->AFR[0] & ~0xFFF00000u)
                  | (5u << 20u) | (5u << 24u) | (5u << 28u);
    GPIOA->OSPEEDR |= (0x03u << (5u * 2u)) | (0x03u << (7u * 2u));
    cs_high();
}

static bool flash_status(uint8_t *sr)
{
    uint8_t dummy = 0;
    cs_low();
    bool ok = spi_xfer(CMD_RDSR, &dummy) && spi_xfer(0xFFu, sr);
    cs_high();
    return ok;
}

static void flash_abort(void)
{
    DMA1_Channel3->CCR &= ~DMA_CCR_EN;
    SPI1->CR2 &= ~SPI_CR2_TXDMAEN;
    spi_drain_rx();
    cs_high();
    s_errors++;
    s_state = ST_IDLE;
    release_lock();
}

/* ---- хуки диспетчера ------------------------------------------------------ */

static bool flash_pre_sleep(pm_mode_t target_mode)
{
    if (s_state != ST_IDLE) {
        return false; /* під час запису мікросхему не чіпаємо */
    }
    if (target_mode < PM_MODE_STOP) {
        return true;  /* у SLEEP тактування SPI не зникає */
    }

    /* Одна команда — це кілька тактів на 10 МГц, у бюджет входу в сон вкладається. */
    cs_low();
    bool ok = spi_xfer(CMD_DPD, NULL);
    cs_high();
    if (!ok) {
        return false; /* шина не відповіла — краще не засинати з живою мікросхемою */
    }

    /* Ізоляція виводів: аналоговий стан прибирає струм через підтяжки
     * і паразитне живлення мікросхеми через захисні діоди. */
    s_saved_moder = GPIOA->MODER;
    GPIOA->MODER |= (0x03u << (4u * 2u)) | (0x03u << (5u * 2u))
                  | (0x03u << (6u * 2u)) | (0x03u << (7u * 2u));
    RCC->APB2ENR &= ~RCC_APB2ENR_SPI1EN;
    s_deep_power_down = true;
    return true;
}

static void flash_post_wakeup(pm_mode_t from_mode)
{
    (void)from_mode;
    if (!s_deep_power_down) {
        return;
    }
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    (void)RCC->APB2ENR;
    /* Регістри SPI1 переживають STOP, тож відновлюємо лише виводи. */
    GPIOA->MODER = s_saved_moder;
    cs_high();

    cs_low();
    (void)spi_xfer(CMD_RES, NULL);
    cs_high();
    for (uint32_t i = 0; i < RES_SPINS; ++i) {
        __NOP(); /* витримка tRES1 до першої робочої команди */
    }
    s_deep_power_down = false;
}

static const pm_driver_client_t s_flash_client = {
    .name        = "SPI-Flash",
    .pre_sleep   = flash_pre_sleep,
    .post_wakeup = flash_post_wakeup,
};

/* ---- публічний інтерфейс -------------------------------------------------- */

void spi_flash_init(void)
{
    RCC->AHB2ENR |= RCC_AHB2ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_SPI1EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_DMA1EN;
    (void)RCC->AHB1ENR;

    spi_pins_active();

    /* Майстер, fPCLK/8 = 10 МГц, програмний NSS, кадр 8 бітів, поріг FIFO 1 байт */
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_SSM | SPI_CR1_SSI | (2u << SPI_CR1_BR_Pos);
    SPI1->CR2 = SPI_CR2_FRXTH | (7u << SPI_CR2_DS_Pos);
    SPI1->CR1 |= SPI_CR1_SPE;

    /* DMA1 канал 3 — це SPI1_TX (C3S = 1) */
    DMA1_CSELR->CSELR = (DMA1_CSELR->CSELR & ~DMA_CSELR_C3S) | (1u << DMA_CSELR_C3S_Pos);
    DMA1_Channel3->CPAR = (uint32_t)(volatile void *)&SPI1->DR;
    DMA1_Channel3->CCR  = DMA_CCR_DIR | DMA_CCR_MINC | DMA_CCR_TCIE | DMA_CCR_TEIE;
    NVIC_SetPriority(DMA1_Channel3_IRQn, 2);
    NVIC_EnableIRQ(DMA1_Channel3_IRQn);

    s_state = ST_IDLE;
    pm_register_client(&s_flash_client);
}

bool spi_flash_write_page_async(uint32_t address, const uint8_t *data, size_t len)
{
    if (!data || len == 0u || len > SPI_FLASH_PAGE_SIZE || s_state != ST_IDLE) {
        return false;
    }
    if ((address % SPI_FLASH_PAGE_SIZE) + len > SPI_FLASH_PAGE_SIZE) {
        return false; /* мікросхема загорнула б адресу по колу всередині сторінки */
    }

    /* Блокування береться ДО першої команди й тримається до кінця циклу запису. */
    pm_lock_acquire(PM_LOCK_NO_STOP);
    s_locked = true;

    cs_low();
    bool ok = spi_xfer(CMD_WREN, NULL);
    cs_high();
    if (!ok) {
        s_state = ST_IDLE;
        release_lock();
        return false;
    }

    cs_low();
    ok = spi_xfer(CMD_PP, NULL)
      && spi_xfer((uint8_t)(address >> 16), NULL)
      && spi_xfer((uint8_t)(address >> 8), NULL)
      && spi_xfer((uint8_t)address, NULL);
    if (!ok) {
        cs_high();
        s_state = ST_IDLE;
        release_lock();
        return false;
    }

    s_state = ST_DMA;
    DMA1_Channel3->CCR  &= ~DMA_CCR_EN;
    DMA1_Channel3->CMAR  = (uint32_t)data;
    DMA1_Channel3->CNDTR = (uint32_t)len;
    DMA1->IFCR = DMA_IFCR_CGIF3;
    DMA1_Channel3->CCR |= DMA_CCR_EN;
    SPI1->CR2 |= SPI_CR2_TXDMAEN;
    return true;
}

void spi_flash_poll(void)
{
    if (s_state != ST_PROGRAM) {
        return;
    }
    uint8_t sr = 0xFFu;
    if (!flash_status(&sr)) {
        s_state = ST_IDLE;
        release_lock();
        return;
    }
    if ((sr & SR_WIP) == 0u) {
        s_state = ST_IDLE;
        release_lock(); /* аж тепер глибокий сон безпечний */
    }
}

bool spi_flash_busy(void)
{
    return s_state != ST_IDLE;
}

uint32_t spi_flash_errors(void)
{
    return s_errors;
}

void DMA1_Channel3_IRQHandler(void)
{
    uint32_t isr = DMA1->ISR;

    if ((isr & DMA_ISR_TEIF3) != 0u) {
        DMA1->IFCR = DMA_IFCR_CGIF3;
        flash_abort();
        return;
    }
    if ((isr & DMA_ISR_TCIF3) == 0u) {
        return;
    }
    DMA1->IFCR = DMA_IFCR_CGIF3;
    DMA1_Channel3->CCR &= ~DMA_CCR_EN;
    SPI1->CR2 &= ~SPI_CR2_TXDMAEN;

    /* DMA скінчив віддавати байти в FIFO, але зсувний регістр ще жене останній:
     * зняти CS раніше за BSY означає обрубати кадр. */
    uint32_t spins = SPI_SPINS;
    while ((SPI1->SR & SPI_SR_BSY) != 0u && spins-- != 0u) {
    }
    spi_drain_rx();
    cs_high();

    /* Блокування НЕ знімаємо: мікросхема ще пече сторінку (до 3 мс),
     * і команда Deep Power-Down у цей час її зіпсує. Знімає spi_flash_poll(). */
    s_state = ST_PROGRAM;
}
