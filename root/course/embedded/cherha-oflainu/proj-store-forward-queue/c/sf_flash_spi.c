#include "sf_flash_spi.h"

#include <string.h>

/* Команди сімейства W25Q — однакові в усіх виробників клонів. */
#define CMD_WRITE_ENABLE 0x06u
#define CMD_READ_STATUS1 0x05u
#define CMD_READ_DATA    0x03u
#define CMD_PAGE_PROGRAM 0x02u
#define CMD_SECTOR_ERASE 0x20u
#define CMD_JEDEC_ID     0x9Fu

#define STATUS_BUSY 0x01u
#define STATUS_WEL  0x02u

/* Паспортні максимуми W25Q128: сторінка 3 мс, сектор 400 мс.
 * Беремо з запасом — і все одно виходимо по таймауту, а не зависаємо. */
#define TIMEOUT_PROGRAM_MS 10u
#define TIMEOUT_ERASE_MS   800u

#define PAGE_SIZE   256u
#define SECTOR_SIZE 4096u

static bool cmd_only(sf_flash_spi_t *fl, uint8_t cmd)
{
    bool ok;

    fl->port.select(fl->port.ctx);
    ok = fl->port.transfer(fl->port.ctx, &cmd, NULL, 1);
    fl->port.deselect(fl->port.ctx);
    return ok;
}

static bool read_status(sf_flash_spi_t *fl, uint8_t *status)
{
    const uint8_t cmd = CMD_READ_STATUS1;
    bool ok;

    fl->port.select(fl->port.ctx);
    ok = fl->port.transfer(fl->port.ctx, &cmd, NULL, 1) &&
         fl->port.transfer(fl->port.ctx, NULL, status, 1);
    fl->port.deselect(fl->port.ctx);
    return ok;
}

/* Чекаємо зняття BUSY. Опитування статусу — не найкрасивіше, зате
 * працює без переривань і в аварійному режимі, коли планувальник уже
 * зупинено, а журнал ще треба дописати. */
static sf_flash_err_t wait_ready(sf_flash_spi_t *fl, uint32_t timeout_ms)
{
    const uint32_t start = fl->port.now_ms(fl->port.ctx);

    for (;;) {
        uint8_t status = 0;

        if (!read_status(fl, &status)) {
            return SF_FLASH_EIO;
        }
        if ((status & STATUS_BUSY) == 0u) {
            return SF_FLASH_OK;
        }
        if ((fl->port.now_ms(fl->port.ctx) - start) > timeout_ms) {
            return SF_FLASH_ETIME;
        }
    }
}

/* WREN скидається сам після кожної операції запису, тому його треба
 * ставити щоразу. І щоразу ж перевіряти, що біт справді піднявся:
 * мовчазне ігнорування WREN — класична ознака непропаяного CS. */
static sf_flash_err_t write_enable(sf_flash_spi_t *fl)
{
    uint8_t status = 0;

    if (!cmd_only(fl, CMD_WRITE_ENABLE)) {
        return SF_FLASH_EIO;
    }
    if (!read_status(fl, &status)) {
        return SF_FLASH_EIO;
    }
    return ((status & STATUS_WEL) != 0u) ? SF_FLASH_OK : SF_FLASH_EIO;
}

static void fill_addr(uint8_t *frame, uint8_t cmd, uint32_t addr)
{
    frame[0] = cmd;
    frame[1] = (uint8_t)((addr >> 16) & 0xFFu);
    frame[2] = (uint8_t)((addr >> 8) & 0xFFu);
    frame[3] = (uint8_t)(addr & 0xFFu);
}

static sf_flash_err_t spi_read(void *ctx, uint32_t addr, void *dst, uint32_t len)
{
    sf_flash_spi_t *fl = (sf_flash_spi_t *)ctx;
    uint8_t frame[4];
    bool ok;

    if (addr + len > fl->capacity) {
        return SF_FLASH_EPARAM;
    }

    /* Читати можна й під час чужої операції — але прочитаємо сміття.
     * Дешевше зачекати. */
    sf_flash_err_t err = wait_ready(fl, TIMEOUT_ERASE_MS);
    if (err != SF_FLASH_OK) {
        return err;
    }

    fill_addr(frame, CMD_READ_DATA, addr);
    fl->port.select(fl->port.ctx);
    ok = fl->port.transfer(fl->port.ctx, frame, NULL, sizeof(frame)) &&
         fl->port.transfer(fl->port.ctx, NULL, (uint8_t *)dst, len);
    fl->port.deselect(fl->port.ctx);

    return ok ? SF_FLASH_OK : SF_FLASH_EIO;
}

static sf_flash_err_t program_page(sf_flash_spi_t *fl, uint32_t addr,
                                   const uint8_t *src, uint32_t len)
{
    uint8_t frame[4];
    bool ok;

    sf_flash_err_t err = write_enable(fl);
    if (err != SF_FLASH_OK) {
        return err;
    }

    fill_addr(frame, CMD_PAGE_PROGRAM, addr);
    fl->port.select(fl->port.ctx);
    ok = fl->port.transfer(fl->port.ctx, frame, NULL, sizeof(frame)) &&
         fl->port.transfer(fl->port.ctx, src, NULL, len);
    fl->port.deselect(fl->port.ctx);

    if (!ok) {
        return SF_FLASH_EIO;
    }
    return wait_ready(fl, TIMEOUT_PROGRAM_MS);
}

static sf_flash_err_t spi_program(void *ctx, uint32_t addr, const void *src, uint32_t len)
{
    sf_flash_spi_t *fl = (sf_flash_spi_t *)ctx;
    const uint8_t *p = (const uint8_t *)src;

    if (addr + len > fl->capacity) {
        return SF_FLASH_EPARAM;
    }

    /* Ось те місце, заради якого драйвер узагалі існує: кадр черги
     * (до 536 байтів) майже завжди перетинає межу сторінки, і мікросхема
     * розірве його сама — тихо й неправильно. Ріжемо тут. */
    while (len > 0u) {
        const uint32_t page_left = PAGE_SIZE - (addr % PAGE_SIZE);
        const uint32_t chunk = (len < page_left) ? len : page_left;

        sf_flash_err_t err = program_page(fl, addr, p, chunk);
        if (err != SF_FLASH_OK) {
            return err;
        }

        addr += chunk;
        p += chunk;
        len -= chunk;
    }
    return SF_FLASH_OK;
}

static sf_flash_err_t spi_erase_sector(void *ctx, uint32_t addr)
{
    sf_flash_spi_t *fl = (sf_flash_spi_t *)ctx;
    uint8_t frame[4];
    bool ok;

    if (addr + SECTOR_SIZE > fl->capacity) {
        return SF_FLASH_EPARAM;
    }

    sf_flash_err_t err = write_enable(fl);
    if (err != SF_FLASH_OK) {
        return err;
    }

    fill_addr(frame, CMD_SECTOR_ERASE, addr);
    fl->port.select(fl->port.ctx);
    ok = fl->port.transfer(fl->port.ctx, frame, NULL, sizeof(frame));
    fl->port.deselect(fl->port.ctx);

    if (!ok) {
        return SF_FLASH_EIO;
    }
    return wait_ready(fl, TIMEOUT_ERASE_MS);
}

bool sf_flash_spi_init(sf_flash_spi_t *fl, const sf_spi_port_t *port,
                       uint32_t capacity, sf_flash_dev_t *dev)
{
    const uint8_t cmd = CMD_JEDEC_ID;
    bool ok;

    memset(fl, 0, sizeof(*fl));
    fl->port = *port;
    fl->capacity = capacity;

    fl->port.select(fl->port.ctx);
    ok = fl->port.transfer(fl->port.ctx, &cmd, NULL, 1) &&
         fl->port.transfer(fl->port.ctx, NULL, fl->jedec_id, sizeof(fl->jedec_id));
    fl->port.deselect(fl->port.ctx);

    if (!ok) {
        return false;
    }
    /* 0x00 і 0xFF — це не ідентифікатори, а мовчазна шина: або CS висить
     * у повітрі, або мікросхема не запитана. */
    if (fl->jedec_id[0] == 0x00u || fl->jedec_id[0] == 0xFFu) {
        return false;
    }

    dev->read = spi_read;
    dev->program = spi_program;
    dev->erase_sector = spi_erase_sector;
    dev->ctx = fl;
    dev->sector_size = SECTOR_SIZE;
    dev->page_size = PAGE_SIZE;
    dev->capacity = capacity;
    return true;
}
