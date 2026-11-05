#include <stdint.h>
#include <stdbool.h>

#define FLASH_KEY1               0x45670123U
#define FLASH_KEY2               0xCDEF89ABU

#define FLASH_REG_ACR            (*(volatile uint32_t *)0x40023C00U)
#define FLASH_REG_KEYR           (*(volatile uint32_t *)0x40023C04U)
#define FLASH_REG_SR             (*(volatile uint32_t *)0x40023C0CU)
#define FLASH_REG_CR             (*(volatile uint32_t *)0x40023C10U)

#define FLASH_CR_PG              (1U << 0)
#define FLASH_CR_SER             (1U << 1)
#define FLASH_CR_STRT            (1U << 16)
#define FLASH_CR_LOCK            (1U << 31)
#define FLASH_CR_SNB_POS         3U
#define FLASH_CR_SNB_MASK        (0x1FU << FLASH_CR_SNB_POS)

#define FLASH_SR_BSY             (1U << 16)
#define FLASH_SR_EOP             (1U << 0)
#define FLASH_SR_PGSERR          (1U << 7)
#define FLASH_SR_WRPERR          (1U << 4)

#define FLASH_ACR_ICEN           (1U << 9)
#define FLASH_ACR_DCEN           (1U << 10)
#define FLASH_ACR_ICRST          (1U << 11)
#define FLASH_ACR_DCRST          (1U << 12)

#define LBA_SECTOR_SIZE          512U
#define FLASH_SECTOR_SIZE_BYTES  2048U

typedef enum {
    BUF_STATE_EMPTY,
    BUF_STATE_FILLING,
    BUF_STATE_READY,
    BUF_STATE_WRITING
} buffer_state_t;

typedef struct {
    uint8_t data[LBA_SECTOR_SIZE];
    volatile buffer_state_t state;
    uint32_t flash_offset;
} ping_pong_buffer_t;

static ping_pong_buffer_t g_buffers[2];
static volatile uint8_t g_rx_index = 0;
static volatile uint8_t g_flash_index = 0;

extern void bsp_watchdog_feed(void);
extern void bsp_usb_set_endpoint_nak(uint8_t ep_num, bool nak);

// Розблокування регістрів Flash
static void flash_unlock(void) {
    if ((FLASH_REG_CR & FLASH_CR_LOCK) != 0U) {
        FLASH_REG_KEYR = FLASH_KEY1;
        FLASH_REG_KEYR = FLASH_KEY2;
    }
}

// Блокування регістрів Flash
static void flash_lock(void) {
    FLASH_REG_CR |= FLASH_CR_LOCK;
}

// Примусове скидання та оновлення кешу інструкцій і даних
static void flash_cache_flush(void) {
    FLASH_REG_ACR &= ~(FLASH_ACR_ICEN | FLASH_ACR_DCEN);
    FLASH_REG_ACR |= (FLASH_ACR_ICRST | FLASH_ACR_DCRST);
    FLASH_REG_ACR &= ~(FLASH_ACR_ICRST | FLASH_ACR_DCRST);
    FLASH_REG_ACR |= (FLASH_ACR_ICEN | FLASH_ACR_DCEN);
}

// Очікування завершення апаратної операції контролера Flash
static bool flash_wait_ready(void) {
    while ((FLASH_REG_SR & FLASH_SR_BSY) != 0U) {
        bsp_watchdog_feed();
    }
    if ((FLASH_REG_SR & (FLASH_SR_PGSERR | FLASH_SR_WRPERR)) != 0U) {
        FLASH_REG_SR |= (FLASH_SR_PGSERR | FLASH_SR_WRPERR);
        return false;
    }
    return true;
}

// Високовольтне стирання сектора за його порядковим номером
bool flash_erase_sector(uint8_t sector_num) {
    flash_unlock();
    if (!flash_wait_ready()) {
        flash_lock();
        return false;
    }
    FLASH_REG_CR &= ~FLASH_CR_SNB_MASK;
    FLASH_REG_CR |= FLASH_CR_SER | ((uint32_t)sector_num << FLASH_CR_SNB_POS);
    FLASH_REG_CR |= FLASH_CR_STRT;

    bool success = flash_wait_ready();
    FLASH_REG_CR &= ~FLASH_CR_SER;
    flash_lock();
    flash_cache_flush();
    return success;
}

// Запис 32-бітного слова у комірку пам'яті
bool flash_program_word(uint32_t address, uint32_t word) {
    flash_unlock();
    if (!flash_wait_ready()) {
        flash_lock();
        return false;
    }
    FLASH_REG_CR |= FLASH_CR_PG;
    *(volatile uint32_t *)address = word;

    bool success = flash_wait_ready();
    FLASH_REG_CR &= ~FLASH_CR_PG;
    flash_lock();
    return success;
}

// Обробник переривання приймання пакета USB Bulk-Out
void usb_bulk_out_isr_handler(const uint8_t *packet, uint32_t length, uint32_t lba_offset) {
    ping_pong_buffer_t *current_buf = &g_buffers[g_rx_index];
    if (current_buf->state == BUF_STATE_EMPTY) {
        current_buf->state = BUF_STATE_FILLING;
        current_buf->flash_offset = lba_offset;
        for (uint32_t i = 0; i < length; ++i) {
            current_buf->data[i] = packet[i];
        }
        current_buf->state = BUF_STATE_READY;
        g_rx_index = (g_rx_index == 0U) ? 1U : 0U;

        // Якщо наступний буфер зайнятий записом, виставляємо NAK для шини
        if (g_buffers[g_rx_index].state != BUF_STATE_EMPTY) {
            bsp_usb_set_endpoint_nak(1U, true);
        }
    }
}

// Фонові виклики конвеєра запису в головному циклі
void flash_pipeline_process(uint32_t app_base_addr) {
    ping_pong_buffer_t *target_buf = &g_buffers[g_flash_index];
    if (target_buf->state == BUF_STATE_READY) {
        target_buf->state = BUF_STATE_WRITING;
        uint32_t target_addr = app_base_addr + target_buf->flash_offset;

        // Початок апаратного сектора вимагає попереднього стирання
        if ((target_addr % FLASH_SECTOR_SIZE_BYTES) == 0U) {
            uint8_t sector_num = (uint8_t)(target_buf->flash_offset / FLASH_SECTOR_SIZE_BYTES);
            flash_erase_sector(sector_num);
        }

        const uint32_t *words = (const uint32_t *)target_buf->data;
        for (uint32_t i = 0; i < (LBA_SECTOR_SIZE / 4U); ++i) {
            flash_program_word(target_addr + (i * 4U), words[i]);
        }

        target_buf->state = BUF_STATE_EMPTY;
        bsp_usb_set_endpoint_nak(1U, false);
        g_flash_index = (g_flash_index == 0U) ? 1U : 0U;
    }
}
