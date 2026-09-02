#include <inttypes.h>
#include <stdio.h>

#include "jedec.h"
#include "sfdp.h"

/* Платформа цього прикладу — симулятор кристала. Один конструктор окремого
   заголовка не вартий. */
spi_port_t *sim_w25q_create(void);

static void print_raw(const char *label, const uint8_t *raw, unsigned len)
{
    printf("%s:", label);
    for (unsigned i = 0; i < len; ++i) {
        printf(" %02X", raw[i]);
    }
    printf("\n");
}

/* Так виглядає перша спокуса: викликати 0x9F на робочій частоті й повірити
   тому, що прийшло. */
static void naive_probe(spi_port_t *port)
{
    const uint8_t cmd = JEDEC_CMD_READ_ID;
    uint8_t raw[JEDEC_ID_MAX_BYTES];
    flash_passport_t passport;

    spi_command(port, &cmd, 1, raw, sizeof raw);
    printf("— наївне опитування на %" PRIu32 " Гц —\n", port->clock_hz(port));
    print_raw("  сира відповідь", raw, (unsigned)sizeof raw);
    printf("  діагноз: %s\n\n",
           jedec_status_text(jedec_decode(raw, (uint8_t)sizeof raw, &passport)));
}

static void print_passport(const flash_passport_t *p)
{
    print_raw("  сира відповідь", p->raw, p->raw_len);
    printf("  банк JEP106:     %u\n", p->bank);
    printf("  виробник:        0x%02X — %s\n", p->manufacturer_id, p->vendor_name);
    printf("  тип пам'яті:     0x%02X\n", p->memory_type);
    printf("  код ємності:     0x%02X\n", p->capacity_id);
    printf("  обсяг:           %" PRIu32 " Б (%" PRIu32 " Мбіт)\n",
           p->total_size_bytes, (uint32_t)(p->total_size_bytes / 131072u));
    printf("  сторінок по %" PRIu32 ": %" PRIu32 "\n", p->page_size_bytes, p->total_pages);
    printf("  секторів по %" PRIu32 ": %" PRIu32 "\n", p->sector_size_bytes, p->total_sectors);
    printf("  вихід із QPI:    %s\n", p->qpi_recovered ? "знадобився" : "не знадобився");
}

static void print_sfdp(const sfdp_params_t *s)
{
    printf("  ревізія:         JESD216, %u.%u, таблиця %u подвійних слів\n",
           s->major, s->minor, s->dwords);
    printf("  адресація:       %u байти%s\n",
           s->address_bytes, s->four_byte_capable ? " (уміє й чотирибайтову)" : "");
    printf("  щільність:       %" PRIu64 " біт = %" PRIu64 " Б\n",
           s->density_bits, s->density_bytes);
    printf("  сторінка:        %" PRIu32 " Б\n", s->page_size_bytes);
    if (s->has_1_4_4) {
        printf("  швидке 1-4-4:    опкод 0x%02X, %u холостих тактів, %u тактів режиму\n",
               s->op_1_4_4, s->dummy_1_4_4, s->mode_1_4_4);
    }
    if (s->has_1_1_4) {
        printf("  швидке 1-1-4:    опкод 0x%02X, %u холостих тактів, %u тактів режиму\n",
               s->op_1_1_4, s->dummy_1_1_4, s->mode_1_1_4);
    }
    for (unsigned i = 0; i < SFDP_ERASE_TYPES; ++i) {
        if (s->erase[i].opcode == 0 && s->erase[i].size_bytes == 0) {
            continue;
        }
        printf("  стирання %u:      %" PRIu32 " Б опкодом 0x%02X, типово %" PRIu32 " мс\n",
               i + 1, s->erase[i].size_bytes, s->erase[i].opcode, s->erase[i].typical_ms);
    }
    printf("  Quad Enable:     %s\n", sfdp_quad_enable_text(s->quad_enable));
}

/* Перевірка самого розбору: відповідь із двома байтами продовження — виробник
   із третього банку JEP106, у нашій таблиці його немає, і це нормально. */
static void continuation_selftest(void)
{
    const uint8_t answer[JEDEC_ID_MAX_BYTES] = { 0x7F, 0x7F, 0x1F, 0x87, 0x18, 0xFF };
    flash_passport_t p;
    const jedec_status_t st = jedec_decode(answer, (uint8_t)sizeof answer, &p);

    printf("— розбір банків продовження —\n");
    print_raw("  сира відповідь", answer, (unsigned)sizeof answer);
    printf("  статус: %s\n", jedec_status_text(st));
    printf("  банк %u, виробник 0x%02X (%s), обсяг %" PRIu32 " Б\n\n",
           p.bank, p.manufacturer_id, p.vendor_name, p.total_size_bytes);
}

/* І окремо — чому bring-up роблять на зниженій частоті. */
static void clock_limit_demo(spi_port_t *port)
{
    const uint8_t cmd = JEDEC_CMD_READ_ID;
    uint8_t raw[3];
    const uint32_t saved = port->clock_hz(port);

    const uint32_t fast = port->set_clock_hz(port, 80000000u);
    spi_command(port, &cmd, 1, raw, sizeof raw);
    printf("— те саме опитування на %" PRIu32 " Гц —\n", fast);
    print_raw("  сира відповідь", raw, (unsigned)sizeof raw);
    printf("  опкод 0x9F обмежений 33–50 МГц: биті такти читаються як нулі\n\n");
    port->set_clock_hz(port, saved);
}

int main(void)
{
    spi_port_t *port = sim_w25q_create();
    flash_passport_t passport;
    sfdp_params_t params;

    naive_probe(port);

    printf("— опитування за протоколом —\n");
    const jedec_status_t id_status = jedec_identify(port, &passport);
    printf("  статус: %s\n", jedec_status_text(id_status));
    print_passport(&passport);
    if (id_status != JEDEC_OK) {
        return 1;
    }
    printf("\n— таблиця параметрів SFDP —\n");
    const sfdp_status_t sfdp_status = sfdp_read(port, &params);
    printf("  статус: %s\n", sfdp_status_text(sfdp_status));
    if (sfdp_status != SFDP_OK) {
        return 1;
    }
    print_sfdp(&params);

    printf("\n");
    clock_limit_demo(port);
    continuation_selftest();

    /* Два незалежні джерела обсягу мусять зійтися. Розбіжність означає, що
       код ємності й таблиця параметрів описують різні кристали, — типова
       ознака перемаркованої мікросхеми. */
    printf("— звірення джерел обсягу —\n");
    printf("  код ємності 0x%02X: %" PRIu32 " Б\n", passport.capacity_id, passport.total_size_bytes);
    printf("  щільність SFDP:   %" PRIu64 " Б\n", params.density_bytes);
    if ((uint64_t)passport.total_size_bytes != params.density_bytes) {
        printf("  ✖ джерела розходяться: кристал перемаркований або відповідь спотворена\n");
        return 1;
    }
    printf("  ✓ джерела збігаються, геометрію можна брати в роботу\n");
    return 0;
}
