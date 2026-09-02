#include "sfdp.h"

#include <string.h>

/* Читання таблиці параметрів: опкод, три байти адреси всередині SFDP-ROM
   і обов'язковий холостий такт перед даними. */
static void sfdp_read_bytes(spi_port_t *port, uint32_t addr, uint8_t *dst, size_t len)
{
    const uint8_t cmd[5] = {
        SFDP_CMD_READ,
        (uint8_t)(addr >> 16),
        (uint8_t)(addr >> 8),
        (uint8_t)addr,
        0x00  /* dummy byte */
    };
    memset(dst, 0, len);
    spi_command(port, cmd, sizeof cmd, dst, len);
}

static uint32_t le32(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

const char *sfdp_status_text(sfdp_status_t status)
{
    switch (status) {
    case SFDP_OK:                 return "таблицю параметрів прочитано";
    case SFDP_ERR_SIGNATURE:      return "сигнатури SFDP немає: кристал стандарту не підтримує";
    case SFDP_ERR_NO_BASIC_TABLE: return "базової таблиці параметрів у заголовках немає";
    case SFDP_ERR_TRUNCATED:      return "таблиця коротша за обов'язкові поля";
    default:                      return "невідомий стан";
    }
}

const char *sfdp_quad_enable_text(uint8_t qer)
{
    switch (qer) {
    case 0: return "біта QE немає: чотирилінійні команди вмикаються самим опкодом";
    case 1: return "QE — біт 1 у SR2, запис командою 0x01 двома байтами";
    case 2: return "QE — біт 6 у SR1, запис командою 0x01 одним байтом";
    case 3: return "QE — біт 7 у SR2, читання 0x3F, запис 0x3E";
    case 4: return "QE — біт 1 у SR2, читання 0x35, запис 0x01 двома байтами";
    case 5: return "QE — біт 1 у SR2, читання 0x35, запис 0x31 одним байтом";
    default: return "схема QE нестандартна або таблиця її не оголошує";
    }
}

/* Часи стирання в DWORD10 упаковані по 7 бітів на тип: п'ять бітів лічильника
   й два біти одиниці виміру. Час = (лічильник + 1) × одиниця. */
static uint32_t erase_time_ms(uint32_t dword10, unsigned index)
{
    static const uint32_t unit_ms[4] = { 1u, 16u, 128u, 1000u };
    const uint32_t field = (dword10 >> (4u + 7u * index)) & 0x7Fu;
    return ((field & 0x1Fu) + 1u) * unit_ms[(field >> 5) & 0x3u];
}

static void parse_erase_types(sfdp_params_t *out, const uint32_t *dw, unsigned count)
{
    const uint8_t sizes[SFDP_ERASE_TYPES] = {
        (uint8_t)(dw[7] & 0xFFu), (uint8_t)((dw[7] >> 16) & 0xFFu),
        (uint8_t)(dw[8] & 0xFFu), (uint8_t)((dw[8] >> 16) & 0xFFu)
    };
    const uint8_t ops[SFDP_ERASE_TYPES] = {
        (uint8_t)((dw[7] >> 8) & 0xFFu), (uint8_t)((dw[7] >> 24) & 0xFFu),
        (uint8_t)((dw[8] >> 8) & 0xFFu), (uint8_t)((dw[8] >> 24) & 0xFFu)
    };

    for (unsigned i = 0; i < SFDP_ERASE_TYPES; ++i) {
        if (sizes[i] == 0) {
            continue;  /* нульовий степінь означає «типу немає» */
        }
        out->erase[i].opcode     = ops[i];
        out->erase[i].size_bytes = 1UL << sizes[i];
        out->erase[i].typical_ms = (count >= 10) ? erase_time_ms(dw[9], i) : 0;
    }
}

sfdp_status_t sfdp_read(spi_port_t *port, sfdp_params_t *out)
{
    uint8_t header[8];

    memset(out, 0, sizeof *out);
    out->page_size_bytes = 256;
    out->address_bytes   = 3;
    out->quad_enable     = 0xFF;

    sfdp_read_bytes(port, 0, header, sizeof header);
    if (header[0] != 'S' || header[1] != 'F' || header[2] != 'D' || header[3] != 'P') {
        return SFDP_ERR_SIGNATURE;
    }
    out->minor = header[4];
    out->major = header[5];

    /* Байт 6 — кількість заголовків параметрів мінус один. Шукаємо серед них
       базову таблицю: молодший байт ідентифікатора 0x00, старший 0xFF. */
    const unsigned headers = (unsigned)header[6] + 1u;
    uint32_t table_addr = 0;
    uint8_t  table_dwords = 0;
    for (unsigned i = 0; i < headers; ++i) {
        uint8_t ph[8];
        sfdp_read_bytes(port, 8u + 8u * i, ph, sizeof ph);
        if (ph[0] == 0x00 && ph[7] == 0xFF) {
            table_dwords = ph[3];
            table_addr   = (uint32_t)ph[4] | ((uint32_t)ph[5] << 8) | ((uint32_t)ph[6] << 16);
            break;
        }
    }
    if (table_dwords == 0) {
        return SFDP_ERR_NO_BASIC_TABLE;
    }
    /* Типи стирання лежать у DWORD8 і DWORD9 — коротша таблиця нам не годиться. */
    if (table_dwords < 9) {
        return SFDP_ERR_TRUNCATED;
    }

    const unsigned count = (table_dwords > SFDP_MAX_DWORDS) ? SFDP_MAX_DWORDS : table_dwords;
    uint8_t bytes[SFDP_MAX_DWORDS * 4];
    uint32_t dw[SFDP_MAX_DWORDS];
    sfdp_read_bytes(port, table_addr, bytes, count * 4u);
    for (unsigned i = 0; i < count; ++i) {
        dw[i] = le32(&bytes[i * 4u]);
    }
    out->dwords = (uint8_t)count;

    /* DWORD1: скільки байтів адреси й чи оголошено швидкі чотирилінійні читання. */
    switch ((dw[0] >> 17) & 0x3u) {
    case 0:  out->address_bytes = 3; break;
    case 1:  out->address_bytes = 3; out->four_byte_capable = true; break;
    default: out->address_bytes = 4; out->four_byte_capable = true; break;
    }
    out->has_1_4_4 = (dw[0] & (1UL << 21)) != 0;
    out->has_1_1_4 = (dw[0] & (1UL << 22)) != 0;

    /* DWORD2: щільність. Старший біт скинуто — значення це «кількість бітів
       мінус один», піднято — це степінь двійки в бітах (кристали від 4 Гбіт). */
    if ((dw[1] & 0x80000000UL) == 0) {
        out->density_bits = (uint64_t)dw[1] + 1u;
    } else {
        out->density_bits = (uint64_t)1u << (dw[1] & 0x7FFFFFFFUL);
    }
    out->density_bytes = out->density_bits / 8u;

    /* DWORD3: опкоди й холості такти обох чотирилінійних читань. */
    out->dummy_1_4_4 = (uint8_t)(dw[2] & 0x1Fu);
    out->mode_1_4_4  = (uint8_t)((dw[2] >> 5) & 0x7u);
    out->op_1_4_4    = (uint8_t)((dw[2] >> 8) & 0xFFu);
    out->dummy_1_1_4 = (uint8_t)((dw[2] >> 16) & 0x1Fu);
    out->mode_1_1_4  = (uint8_t)((dw[2] >> 21) & 0x7u);
    out->op_1_1_4    = (uint8_t)((dw[2] >> 24) & 0xFFu);

    parse_erase_types(out, dw, count);

    /* DWORD11: розмір сторінки програмування як степінь двійки. */
    if (count >= 11) {
        out->page_size_bytes = 1UL << ((dw[10] >> 4) & 0xFu);
    }
    /* DWORD15: як саме на цьому кристалі вмикається біт Quad Enable. */
    if (count >= 15) {
        out->quad_enable = (uint8_t)((dw[14] >> 20) & 0x7u);
    }
    return SFDP_OK;
}
