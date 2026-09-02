#include "mcp23017.h"

#include <stddef.h>

/* Мапа регістрів при IOCON.BANK = 0 */
#define REG_IODIRA      0x00u
#define REG_IODIRB      0x01u
#define REG_IPOLA       0x02u
#define REG_GPINTENA    0x04u
#define REG_IOCON_BANK1 0x05u
#define REG_INTCONA     0x08u
#define REG_IOCON       0x0Au
#define REG_GPPUA       0x0Cu
#define REG_INTFA       0x0Eu
#define REG_INTCAPA     0x10u
#define REG_GPIOA       0x12u
#define REG_OLATB       0x15u

/* Біти IOCON */
#define IOCON_MIRROR 0x40u  /* INTA і INTB зводяться в один сигнал */
#define IOCON_ODR    0x04u  /* вихід INT з відкритим стоком — монтажне «АБО» */

/* Скільки повних обходів банку терпимо, поки лінія INT лежить у нулі. */
#define BANK_MAX_PASSES 4u

static io_status_t write_reg(uint8_t addr, uint8_t reg, uint8_t val)
{
    const uint8_t frame[2] = { reg, val };
    return i2c_write(addr, frame, (uint8_t)sizeof frame);
}

static io_status_t read_reg(uint8_t addr, uint8_t reg, uint8_t *val)
{
    return i2c_write_read(addr, &reg, 1u, val, 1u);
}

io_status_t mcp23017_init(mcp23017_t *dev)
{
    io_status_t st;
    uint8_t scratch;

    if (dev == NULL) {
        return IO_ERR_ARG;
    }
    if (dev->addr < MCP23017_ADDR_BASE ||
        dev->addr > (uint8_t)(MCP23017_ADDR_BASE + 7u)) {
        return IO_ERR_ARG;
    }

    /* Чип міг лишитися в мапі BANK = 1 після теплого перезапуску МК. Нуль за
       адресою 0x05 повертає його в BANK = 0, бо в тій мапі 0x05 — це сам
       IOCON. Якщо ж чип уже в BANK = 0, ми записали нуль у GPINTENB: порт B
       у нас під реле, переривань звідти однаково не треба. */
    st = write_reg(dev->addr, REG_IOCON_BANK1, 0x00u);
    if (st != IO_OK) {
        return st;
    }

    st = write_reg(dev->addr, REG_IOCON, IOCON_MIRROR | IOCON_ODR);
    if (st != IO_OK) {
        return st;
    }

    st = write_reg(dev->addr, REG_IODIRA, dev->in_mask);
    if (st != IO_OK) {
        return st;
    }
    st = write_reg(dev->addr, REG_GPPUA, dev->pullup_mask);
    if (st != IO_OK) {
        return st;
    }
    st = write_reg(dev->addr, REG_IPOLA, dev->invert_mask);
    if (st != IO_OK) {
        return st;
    }

    /* INTCON = 0 — переривання за зміною рівня, а не за розбіжністю з
       еталоном DEFVAL: кінцевик цікавить нас в обидва боки. */
    st = write_reg(dev->addr, REG_INTCONA, 0x00u);
    if (st != IO_OK) {
        return st;
    }
    st = write_reg(dev->addr, REG_GPINTENA,
                   (uint8_t)(dev->int_mask & dev->in_mask));
    if (st != IO_OK) {
        return st;
    }

    /* Порт B — вісім виходів реле, усі знеструмлені на старті. */
    st = write_reg(dev->addr, REG_IODIRB, 0x00u);
    if (st != IO_OK) {
        return st;
    }
    st = write_reg(dev->addr, REG_OLATB, 0x00u);
    if (st != IO_OK) {
        return st;
    }
    dev->relay_shadow = 0x00u;

    /* Налаштування піднімало й опускало входи — прапорець уже міг звестися,
       а разом з ним і лінія INT. Знімаємо його читанням INTCAP. */
    return read_reg(dev->addr, REG_INTCAPA, &scratch);
}

io_status_t mcp23017_relays(mcp23017_t *dev, uint8_t mask)
{
    io_status_t st;

    if (dev == NULL) {
        return IO_ERR_ARG;
    }
    st = write_reg(dev->addr, REG_OLATB, mask);
    if (st == IO_OK) {
        dev->relay_shadow = mask;
    }
    return st;
}

io_status_t mcp23017_relay_set(mcp23017_t *dev, uint8_t index, bool on)
{
    uint8_t mask;

    if (dev == NULL || index > 7u) {
        return IO_ERR_ARG;
    }

    /* Тіньова копія рятує від читання-модифікації-запису через шину: саме
       лише читання OLAT коштувало б іще 30 мкс, а стан виходів усе одно
       ніхто, крім мікроконтролера, не міняє. */
    mask = dev->relay_shadow;
    if (on) {
        mask |= (uint8_t)(1u << index);
    } else {
        mask &= (uint8_t)~(1u << index);
    }
    if (mask == dev->relay_shadow) {
        return IO_OK;
    }
    return mcp23017_relays(dev, mask);
}

io_status_t mcp23017_read_inputs(const mcp23017_t *dev, uint8_t *level)
{
    if (dev == NULL || level == NULL) {
        return IO_ERR_ARG;
    }
    return read_reg(dev->addr, REG_GPIOA, level);
}

io_status_t mcp23017_take_event(mcp23017_t *dev, uint8_t *flags,
                                uint8_t *captured)
{
    io_status_t st;

    if (dev == NULL || flags == NULL || captured == NULL) {
        return IO_ERR_ARG;
    }
    *flags = 0u;
    *captured = 0u;

    st = read_reg(dev->addr, REG_INTFA, flags);
    if (st != IO_OK) {
        return st;
    }
    if (*flags == 0u) {
        return IO_OK;  /* спільну лінію тримав не цей чип */
    }

    /* Читаємо саме INTCAP, а не GPIO. У INTCAP лежить зліпок входів на
       мікросекунду перепаду: кнопка вже могла відскочити, і GPIO показав би
       спокій — подія загубилася б. Це ж читання відпускає лінію INT. */
    return read_reg(dev->addr, REG_INTCAPA, captured);
}

bool expander_bank_pending(const expander_bank_t *bank)
{
    if (bank == NULL) {
        return false;
    }
    /* Активний рівень лінії — низький: хоч один чип тягне її до землі. */
    return !gpio_read(bank->int_pin);
}

uint8_t expander_bank_service(expander_bank_t *bank, expander_event_t *out,
                              uint8_t max, io_status_t *status)
{
    io_status_t first = IO_OK;
    uint8_t count = 0u;
    uint8_t pass = 0u;

    if (bank == NULL || bank->chip == NULL || out == NULL ||
        bank->count == 0u || bank->count > MCP23017_MAX_CHIPS) {
        if (status != NULL) {
            *status = IO_ERR_ARG;
        }
        return 0u;
    }

    /* Виходи INT з відкритим стоком зведені разом: поки хоч один чип тримає
       лінію в нулі, спадного фронту на вході EXTI більше не буде. Тому
       обходимо ВЕСЬ банк — і повторюємо, доки підтяжка не підніме лінію. */
    while (!gpio_read(bank->int_pin)) {
        bool drained = false;
        uint8_t i;

        if (pass++ >= BANK_MAX_PASSES) {
            /* Лінія залипла: чип не відпускає її навіть після читання. */
            if (first == IO_OK) {
                first = IO_ERR_BUS;
            }
            break;
        }

        for (i = 0u; i < bank->count; ++i) {
            uint8_t flags = 0u;
            uint8_t captured = 0u;
            io_status_t st = mcp23017_take_event(&bank->chip[i], &flags,
                                                 &captured);
            if (st != IO_OK) {
                /* Німий чип не звільняє нас від обходу решти банку. */
                if (first == IO_OK) {
                    first = st;
                }
                continue;
            }
            if (flags == 0u) {
                continue;
            }

            drained = true;
            if (count < max) {
                out[count].addr = bank->chip[i].addr;
                out[count].flags = flags;
                out[count].captured = captured;
                ++count;
            }
            /* Переповнення буфера подій не страшне: прапорці ми вже зняли,
               а зафіксований стан входів однаково буде в наступній події. */
        }

        if (!drained) {
            /* Лінія в нулі, а зізнаватися нема кому: обірвана підтяжка або
               на монтажне «АБО» повішено ще щось, чого драйвер не знає. */
            if (first == IO_OK) {
                first = IO_ERR_BUS;
            }
            break;
        }
    }

    if (status != NULL) {
        *status = first;
    }
    return count;
}
