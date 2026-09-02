#include "jedec.h"

#include <string.h>

/* Таблиця JEP106. Той самий код у різних банках — різні компанії, тому
   ключ тут завжди пара (банк, код). */
static const struct {
    uint8_t bank;
    uint8_t id;
    const char *name;
} k_vendors[] = {
    { 1, 0xEF, "Winbond Electronics" },
    { 1, 0xC2, "Macronix (MXIC)" },
    { 1, 0xC8, "GigaDevice" },
    { 1, 0x20, "Micron / Numonyx / ST" },
    { 1, 0x01, "Spansion / Cypress / Infineon" },
    { 1, 0xBF, "Microchip / SST" },
    { 1, 0x9D, "ISSI" },
    { 1, 0x85, "Puya Semiconductor" },
    { 1, 0x68, "Boya Microelectronics" },
    { 1, 0x5E, "Zbit Semiconductor" },
};

const char *jedec_vendor_name(uint8_t bank, uint8_t manufacturer_id)
{
    for (size_t i = 0; i < sizeof k_vendors / sizeof k_vendors[0]; ++i) {
        if (k_vendors[i].bank == bank && k_vendors[i].id == manufacturer_id) {
            return k_vendors[i].name;
        }
    }
    return "невідомий виробник";
}

const char *jedec_status_text(jedec_status_t status)
{
    switch (status) {
    case JEDEC_OK:                return "паспорт зчитано";
    case JEDEC_ERR_SHORT_ANSWER:  return "відповідь коротша за три байти";
    case JEDEC_ERR_LINE_HIGH:     return "суцільні 0xFF: обрив MISO, немає живлення або чип у QPI";
    case JEDEC_ERR_LINE_LOW:      return "суцільні 0x00: замикання MISO на землю або утримане скидання";
    case JEDEC_ERR_CONTINUATION:  return "нескінченні байти продовження 0x7F";
    case JEDEC_ERR_BUSY:          return "прапорець WIP не скинувся: кристал досі стирає";
    case JEDEC_ERR_CAPACITY:      return "код ємності поза діапазоном 0x10..0x1A";
    default:                      return "невідомий стан";
    }
}

static bool all_equal(const uint8_t *data, size_t len, uint8_t value)
{
    for (size_t i = 0; i < len; ++i) {
        if (data[i] != value) {
            return false;
        }
    }
    return true;
}

jedec_status_t jedec_decode(const uint8_t *raw, uint8_t len, flash_passport_t *out)
{
    memset(out, 0, sizeof *out);
    out->page_size_bytes   = 256;
    out->sector_size_bytes = 4096;
    out->vendor_name       = "—";

    if (len < 3) {
        return JEDEC_ERR_SHORT_ANSWER;
    }

    out->raw_len = (len > JEDEC_ID_MAX_BYTES) ? JEDEC_ID_MAX_BYTES : len;
    memcpy(out->raw, raw, out->raw_len);

    /* Скільки байтів 0x7F стоїть попереду — стільки банків JEP106 перегорнуто. */
    uint8_t skip = 0;
    while (skip < len && raw[skip] == 0x7F && skip <= JEDEC_MAX_CONTINUATION) {
        ++skip;
    }
    if (skip > JEDEC_MAX_CONTINUATION || (uint8_t)(skip + 3) > len) {
        return JEDEC_ERR_CONTINUATION;
    }

    const uint8_t *body = raw + skip;
    if (all_equal(body, 3, 0xFF)) {
        return JEDEC_ERR_LINE_HIGH;
    }
    if (all_equal(body, 3, 0x00)) {
        return JEDEC_ERR_LINE_LOW;
    }

    out->bank            = (uint8_t)(skip + 1);
    out->manufacturer_id = body[0];
    out->memory_type     = body[1];
    out->capacity_id     = body[2];
    out->vendor_name     = jedec_vendor_name(out->bank, out->manufacturer_id);

    /* Ємність — логарифмічна: код це степінь двійки в байтах. Поза смугою
       0x10..0x1A це або не код ємності, або взагалі не наша відповідь. */
    if (out->capacity_id < 0x10 || out->capacity_id > 0x1A) {
        return JEDEC_ERR_CAPACITY;
    }
    out->total_size_bytes = 1UL << out->capacity_id;
    out->total_pages      = out->total_size_bytes / out->page_size_bytes;
    out->total_sectors    = out->total_size_bytes / out->sector_size_bytes;
    return JEDEC_OK;
}

static void read_id(spi_port_t *port, uint8_t *raw, size_t len)
{
    const uint8_t cmd = JEDEC_CMD_READ_ID;
    memset(raw, 0, len);
    spi_command(port, &cmd, 1, raw, len);
}

/* Вихід із QPI: сам опкод теж мусить піти по чотирьох лініях, інакше кристал
   його просто не почує — у цьому вся пастка стану QPI. */
static void leave_qpi(spi_port_t *port)
{
    const uint8_t cmd = JEDEC_CMD_EXIT_QPI;
    port->select(port);
    port->quad_write(port, &cmd, 1);
    port->release(port);
}

static jedec_status_t wait_not_busy(spi_port_t *port)
{
    const uint8_t cmd = JEDEC_CMD_READ_STATUS1;
    const uint32_t start = port->millis(port);
    for (;;) {
        uint8_t status = 0;
        spi_command(port, &cmd, 1, &status, 1);
        if ((status & JEDEC_STATUS_WIP) == 0) {
            return JEDEC_OK;
        }
        if (port->millis(port) - start > JEDEC_WIP_TIMEOUT_MS) {
            return JEDEC_ERR_BUSY;
        }
    }
}

jedec_status_t jedec_identify(spi_port_t *port, flash_passport_t *out)
{
    uint8_t raw[JEDEC_ID_MAX_BYTES];
    jedec_status_t status;
    bool recovered = false;

    /* Опитування завжди на зниженій частоті: читання даних кристал тягне на
       104–133 МГц, а сам опкод 0x9F у специфікаціях обмежений 33–50 МГц. */
    const uint32_t saved_hz = port->clock_hz(port);
    port->set_clock_hz(port, JEDEC_SAFE_CLOCK_HZ);

    read_id(port, raw, sizeof raw);

    /* Суцільні 0xFF — це або мертва лінія, або живий кристал у QPI. Дешева
       перевірка: одна спроба виходу з QPI й повторне читання. */
    if (all_equal(raw, 3, 0xFF)) {
        leave_qpi(port);
        read_id(port, raw, sizeof raw);
        recovered = !all_equal(raw, 3, 0xFF);
        if (!recovered) {
            status = JEDEC_ERR_LINE_HIGH;
            goto restore;
        }
    }
    if (all_equal(raw, 3, 0x00)) {
        status = JEDEC_ERR_LINE_LOW;
        goto restore;
    }

    /* Кристал говорить — тепер читається й регістр статусу. Якщо всередині
       йде стирання, перший байт відповіді 0x9F може бути спотворений, тож
       чекаємо скидання WIP і питаємо ще раз. */
    status = wait_not_busy(port);
    if (status != JEDEC_OK) {
        goto restore;
    }
    read_id(port, raw, sizeof raw);
    status = jedec_decode(raw, (uint8_t)sizeof raw, out);
    out->qpi_recovered = recovered;

restore:
    if (status != JEDEC_OK) {
        (void)jedec_decode(raw, (uint8_t)sizeof raw, out);
        out->qpi_recovered = recovered;
    }
    port->set_clock_hz(port, saved_hz);
    return status;
}
