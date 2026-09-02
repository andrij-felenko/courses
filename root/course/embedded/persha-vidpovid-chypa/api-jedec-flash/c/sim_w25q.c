/* Симулятор 128-Мбітного кристала SPI NOR: рівно стільки поведінки, скільки
   треба, щоб драйвер зустрів усі три аномалії розділу 5 — кристал, залишений
   попередньою прошивкою в QPI, активний цикл стирання й частотну межу
   опкоду 0x9F. */

#include <stdbool.h>
#include <string.h>

#include "spi_port.h"

#define SIM_ROM_SIZE        256u
#define SIM_TABLE_OFFSET    0x80u
#define SIM_SOURCE_HZ       80000000u   /* тактовий генератор периферії SPI */
#define SIM_ID_MAX_HZ       50000000u   /* межа для опкоду 0x9F за специфікацією */
#define SIM_TICK_MS         5u          /* крок симульованого годинника */
#define SIM_ERASE_UNTIL_MS  120u        /* стирання сектора, розпочате до bring-up */

typedef enum { STAGE_OPCODE, STAGE_ADDR, STAGE_DUMMY, STAGE_DATA } sim_stage_t;
typedef enum { RESP_IDLE, RESP_ID, RESP_STATUS, RESP_ROM, RESP_ZERO } sim_resp_t;

typedef struct {
    spi_port_t port;        /* мусить бути першим полем: назад приводимо вказівник */
    bool       qpi;
    uint32_t   clock_hz;
    uint32_t   now_ms;
    uint32_t   busy_until_ms;
    uint8_t    rom[SIM_ROM_SIZE];

    sim_stage_t stage;
    sim_resp_t  resp;
    uint32_t    addr;
    unsigned    addr_bytes;
    uint32_t    cursor;
    unsigned    id_index;
} sim_flash_t;

/* Паспорт кристала: Winbond, тип 0x40, код ємності 0x18 = 2^24 = 16 МБ. */
static const uint8_t k_id_bytes[3] = { 0xEF, 0x40, 0x18 };

static void put32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)v;
    p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16);
    p[3] = (uint8_t)(v >> 24);
}

/* Часи стирання пакуються по 7 бітів: п'ять бітів лічильника, два — одиниці. */
#define ERASE_TIME(count, units) ((uint32_t)((((units) & 3u) << 5) | ((count) & 0x1Fu)))

static void build_rom(uint8_t *rom)
{
    memset(rom, 0xFF, SIM_ROM_SIZE);

    /* Заголовок SFDP: сигнатура, ревізія 1.6 (JESD216B), один заголовок параметрів. */
    rom[0] = 'S'; rom[1] = 'F'; rom[2] = 'D'; rom[3] = 'P';
    rom[4] = 0x06; rom[5] = 0x01; rom[6] = 0x00; rom[7] = 0xFF;

    /* Заголовок базової таблиці: ID 0xFF00, 16 подвійних слів, вказівник 0x000080. */
    rom[8]  = 0x00; rom[9]  = 0x06; rom[10] = 0x01; rom[11] = 16;
    rom[12] = (uint8_t)SIM_TABLE_OFFSET; rom[13] = 0x00; rom[14] = 0x00; rom[15] = 0xFF;

    uint8_t *t = rom + SIM_TABLE_OFFSET;
    /* Значення підібрані за форматом JESD216B, як у типового 128-Мбітного кристала. */
    put32(t +  0 * 4, 0xFFF920E5u);  /* 4К-стирання опкодом 0x20, трибайтова адреса, є 1-1-4 і 1-4-4 */
    put32(t +  1 * 4, 0x07FFFFFFu);  /* щільність: 0x07FFFFFF + 1 = 134 217 728 біт = 16 МБ */
    put32(t +  2 * 4, 0x6B08EB44u);  /* 1-4-4: 0xEB, 4 холостих такти; 1-1-4: 0x6B, 8 тактів */
    put32(t +  7 * 4, 0x520F200Cu);  /* тип1 4 КБ опкодом 0x20, тип2 32 КБ опкодом 0x52 */
    put32(t +  8 * 4, 0x0000D810u);  /* тип3 64 КБ опкодом 0xD8, тип4 не використовується */
    put32(t +  9 * 4, 0x02u | (ERASE_TIME(2, 1) << 4)    /* 4 КБ  — 48 мс */
                            | (ERASE_TIME(0, 2) << 11)   /* 32 КБ — 128 мс */
                            | (ERASE_TIME(9, 1) << 18)); /* 64 КБ — 160 мс */
    put32(t + 10 * 4, 0xFFFFFF8Cu);  /* сторінка програмування 2^8 = 256 байтів */
    put32(t + 14 * 4, 0x00500000u);  /* QER = 0b101: QE — біт 1 у SR2, читання 0x35, запис 0x31 */
}

static bool sim_busy(const sim_flash_t *s)
{
    return s->now_ms < s->busy_until_ms;
}

static void sim_select(spi_port_t *port)
{
    sim_flash_t *s = (sim_flash_t *)port;
    s->stage      = STAGE_OPCODE;
    s->resp       = RESP_IDLE;
    s->addr       = 0;
    s->addr_bytes = 0;
    s->cursor     = 0;
    s->id_index   = 0;
}

static void sim_release(spi_port_t *port)
{
    sim_flash_t *s = (sim_flash_t *)port;
    s->stage = STAGE_OPCODE;
    s->resp  = RESP_IDLE;
}

static void sim_write_byte(sim_flash_t *s, uint8_t b)
{
    if (s->qpi) {
        return;  /* у QPI однолінійних команд кристал не чує взагалі */
    }
    switch (s->stage) {
    case STAGE_OPCODE:
        switch (b) {
        case 0x9F:
            /* Понад межу зсув бітів зчитується як нулі — класична пастка
               bring-up на максимальній частоті шини. */
            s->resp  = (s->clock_hz > SIM_ID_MAX_HZ) ? RESP_ZERO : RESP_ID;
            s->stage = STAGE_DATA;
            break;
        case 0x05:
            s->resp  = RESP_STATUS;
            s->stage = STAGE_DATA;
            break;
        case 0x5A:
            s->resp  = RESP_IDLE;
            s->stage = STAGE_ADDR;
            break;
        default:
            s->resp  = RESP_IDLE;
            s->stage = STAGE_DATA;
            break;
        }
        break;
    case STAGE_ADDR:
        s->addr = (s->addr << 8) | b;
        if (++s->addr_bytes == 3) {
            s->stage = STAGE_DUMMY;
        }
        break;
    case STAGE_DUMMY:
        /* Холостий такт з'їдено — далі йдуть дані таблиці. */
        s->cursor = s->addr;
        s->resp   = RESP_ROM;
        s->stage  = STAGE_DATA;
        break;
    case STAGE_DATA:
        break;
    }
}

static uint8_t sim_read_byte(sim_flash_t *s)
{
    if (s->qpi) {
        return 0xFF;  /* MISO лишається в неактивному стані */
    }
    switch (s->resp) {
    case RESP_ID: {
        uint8_t v = (s->id_index < sizeof k_id_bytes) ? k_id_bytes[s->id_index] : 0xFF;
        /* Опитування посеред циклу стирання: внутрішній контролер спотворює
           перший байт відповіді. */
        if (s->id_index == 0 && sim_busy(s)) {
            v = 0xFF;
        }
        ++s->id_index;
        return v;
    }
    case RESP_STATUS:
        return sim_busy(s) ? 0x01u : 0x00u;  /* біт 0 — WIP */
    case RESP_ROM: {
        uint8_t v = (s->cursor < SIM_ROM_SIZE) ? s->rom[s->cursor] : 0xFF;
        ++s->cursor;
        return v;
    }
    case RESP_ZERO:
        return 0x00;
    default:
        return 0xFF;
    }
}

static void sim_transfer(spi_port_t *port, const uint8_t *tx, uint8_t *rx, size_t len)
{
    sim_flash_t *s = (sim_flash_t *)port;
    for (size_t i = 0; i < len; ++i) {
        sim_write_byte(s, tx ? tx[i] : 0x00);
        const uint8_t v = sim_read_byte(s);
        if (rx) {
            rx[i] = v;
        }
    }
}

static void sim_quad_write(spi_port_t *port, const uint8_t *tx, size_t len)
{
    sim_flash_t *s = (sim_flash_t *)port;
    for (size_t i = 0; i < len; ++i) {
        if (s->qpi && tx[i] == 0xFF) {
            s->qpi = false;  /* єдина команда, яку кристал у QPI розуміє */
        }
    }
}

static uint32_t sim_set_clock_hz(spi_port_t *port, uint32_t hz)
{
    sim_flash_t *s = (sim_flash_t *)port;
    if (hz == 0) {
        hz = 1;
    }
    uint32_t div = (SIM_SOURCE_HZ + hz - 1u) / hz;  /* дільник округляє частоту вниз */
    if (div == 0) {
        div = 1;
    }
    s->clock_hz = SIM_SOURCE_HZ / div;
    return s->clock_hz;
}

static uint32_t sim_clock_hz(spi_port_t *port)
{
    return ((sim_flash_t *)port)->clock_hz;
}

static uint32_t sim_millis(spi_port_t *port)
{
    sim_flash_t *s = (sim_flash_t *)port;
    s->now_ms += SIM_TICK_MS;  /* кожен запит часу просуває симульований годинник */
    return s->now_ms;
}

spi_port_t *sim_w25q_create(void)
{
    static sim_flash_t sim;  /* один кристал на прогін: купа тут ні до чого */

    memset(&sim, 0, sizeof sim);
    sim.port.select       = sim_select;
    sim.port.release      = sim_release;
    sim.port.transfer     = sim_transfer;
    sim.port.quad_write   = sim_quad_write;
    sim.port.set_clock_hz = sim_set_clock_hz;
    sim.port.clock_hz     = sim_clock_hz;
    sim.port.millis       = sim_millis;

    sim.qpi           = true;                 /* завантажувач лишив кристал у QPI */
    sim.busy_until_ms = SIM_ERASE_UNTIL_MS;   /* і встиг запустити стирання сектора */
    sim.clock_hz      = SIM_SOURCE_HZ / 2u;   /* 40 МГц після скидання периферії */
    build_rom(sim.rom);
    return &sim.port;
}
