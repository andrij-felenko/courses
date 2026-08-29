/* mock_bus.c — реалізація віртуального чипа.
 *
 * Головне правило моку: він мусить бути вредним рівно настільки, наскільки
 * вредний кремній. Мок, що прощає драйверу забутий біт автоінкременту або
 * запис у регістр лише для читання, робить тести зеленими, а плату —
 * мертвою, і це гірше, ніж не мати тестів узагалі.
 */
#include "mock_bus.h"

#include <string.h>

#include "chip_regs.h"

#define MOCK_ERR_NACK (-2)

void mock_bus_reset(mock_bus_ctx_t *mock, uint8_t dev_addr)
{
    memset(mock, 0, sizeof(*mock));
    mock->dev_addr = dev_addr;
    mock->registers[CHIP_REG_WHO_AM_I] = CHIP_WHO_AM_I_VALUE;
}

void mock_poke(mock_bus_ctx_t *mock, uint8_t reg, uint8_t value)
{
    mock->registers[reg & 0x7Fu] = value;
}

uint8_t mock_peek(const mock_bus_ctx_t *mock, uint8_t reg)
{
    return mock->registers[reg & 0x7Fu];
}

void mock_set_raw_xyz(mock_bus_ctx_t *mock, int16_t x, int16_t y, int16_t z)
{
    const int16_t axes[3] = {x, y, z};
    for (int i = 0; i < 3; ++i) {
        mock->registers[CHIP_REG_OUT_X_L + i * 2 + 0] =
            (uint8_t)((uint16_t)axes[i] & 0xFFu);
        mock->registers[CHIP_REG_OUT_X_L + i * 2 + 1] =
            (uint8_t)(((uint16_t)axes[i] >> 8) & 0xFFu);
    }

    /* Якщо попередній відлік так і не забрали, кремній підіймає прапорець
     * перезапису: тест на пропущені дані спирається саме на нього. */
    if ((mock->registers[CHIP_REG_STATUS] & STATUS_ZYXDA) != 0u) {
        mock->registers[CHIP_REG_STATUS] |= STATUS_ZYXOR;
    }
    mock->registers[CHIP_REG_STATUS] |= STATUS_ZYXDA;
}

void mock_set_accel_g(mock_bus_ctx_t *mock, uint8_t range_g,
                      float gx, float gy, float gz)
{
    const float counts_per_g = 32768.0f / (float)range_g;
    const float in[3] = {gx, gy, gz};
    int16_t raw[3];

    for (int i = 0; i < 3; ++i) {
        float counts = in[i] * counts_per_g;
        /* Насичення, а не мовчазне загортання: реальний чип при перевищенні
         * шкали впирається в край діапазону. */
        if (counts > 32767.0f) {
            counts = 32767.0f;
        } else if (counts < -32768.0f) {
            counts = -32768.0f;
        }
        raw[i] = (int16_t)counts;
    }
    mock_set_raw_xyz(mock, raw[0], raw[1], raw[2]);
}

bool mock_last_write(const mock_bus_ctx_t *mock, uint8_t reg, uint8_t *value)
{
    for (uint32_t i = mock->write_count; i > 0u; --i) {
        if (mock->write_log[i - 1u].reg == reg) {
            *value = mock->write_log[i - 1u].val;
            return true;
        }
    }
    return false;
}

uint32_t mock_writes_to(const mock_bus_ctx_t *mock, uint8_t reg)
{
    uint32_t count = 0u;
    for (uint32_t i = 0u; i < mock->write_count; ++i) {
        if (mock->write_log[i].reg == reg) {
            ++count;
        }
    }
    return count;
}

/* Регістри, які кремній не дає перезаписати ззовні. */
static bool reg_is_read_only(uint8_t reg)
{
    if (reg == CHIP_REG_WHO_AM_I || reg == CHIP_REG_STATUS) {
        return true;
    }
    return reg >= CHIP_REG_OUT_X_L && reg <= CHIP_REG_OUT_Z_H;
}

/* Адреса наступного байта пакетної транзакції. Без біта автоінкременту чип
 * не рухає внутрішній вказівник — і віддає шість разів той самий байт. */
static uint8_t next_addr(uint8_t reg, uint16_t index)
{
    if ((reg & CHIP_REG_AUTO_INC) == 0u) {
        return (uint8_t)(reg & 0x7Fu);
    }
    return (uint8_t)(((reg & 0x7Fu) + index) & 0x7Fu);
}

int32_t mock_bus_read(void *user_ctx, uint8_t dev_addr,
                      uint8_t reg, uint8_t *data, uint16_t len)
{
    mock_bus_ctx_t *mock = (mock_bus_ctx_t *)user_ctx;

    ++mock->seq;
    ++mock->read_transactions;

    if (mock->nack_device_address || dev_addr != mock->dev_addr) {
        return MOCK_ERR_NACK; /* на цій адресі ніхто не відповів */
    }
    if (mock->fail_reads_countdown > 0) {
        --mock->fail_reads_countdown;
        return MOCK_ERR_NACK;
    }

    for (uint16_t i = 0; i < len; ++i) {
        /* Обрив рівно на заданому байті: частина буфера вже заповнена
         * сміттям із шини, і драйвер не має права цим сміттям скористатися. */
        if (mock->break_read_at_byte != 0u && i + 1u == mock->break_read_at_byte) {
            mock->break_read_at_byte = 0u;
            return MOCK_ERR_NACK;
        }
        data[i] = mock->registers[next_addr(reg, i)];
    }

    /* Забрали блок даних — прапорець готовності гасне, як у кремнії. */
    uint8_t first = (uint8_t)(reg & 0x7Fu);
    if (first == CHIP_REG_OUT_X_L && len >= 6u) {
        mock->registers[CHIP_REG_STATUS] &= (uint8_t)~(STATUS_ZYXDA | STATUS_ZYXOR);
    }
    return 0;
}

int32_t mock_bus_write(void *user_ctx, uint8_t dev_addr,
                       uint8_t reg, const uint8_t *data, uint16_t len)
{
    mock_bus_ctx_t *mock = (mock_bus_ctx_t *)user_ctx;

    ++mock->seq;
    ++mock->write_transactions;

    if (mock->nack_device_address || dev_addr != mock->dev_addr) {
        return MOCK_ERR_NACK;
    }
    if (mock->fail_writes_countdown > 0) {
        --mock->fail_writes_countdown;
        return MOCK_ERR_NACK;
    }

    for (uint16_t i = 0; i < len; ++i) {
        uint8_t addr = next_addr(reg, i);
        bool applied = !reg_is_read_only(addr);
        if (applied) {
            mock->registers[addr] = data[i];
        }

        if (mock->write_count < MOCK_MAX_WRITE_LOG) {
            mock->write_log[mock->write_count].seq     = mock->seq;
            mock->write_log[mock->write_count].reg     = addr;
            mock->write_log[mock->write_count].val     = data[i];
            mock->write_log[mock->write_count].applied = applied;
            ++mock->write_count;
        } else {
            ++mock->log_overflow;
        }
    }
    return 0;
}

void mock_delay_ms(uint32_t ms)
{
    /* Час на ПК не витрачаємо: уся суть у тому, що набір тестів іде
     * мілісекунди, а не хвилини. Політику пауз перевіряють за лічильниками
     * спроб, а не за годинником. */
    (void)ms;
}

const chip_bus_ops_t *mock_bus_ops(void)
{
    static const chip_bus_ops_t ops = {
        .read     = mock_bus_read,
        .write    = mock_bus_write,
        .delay_ms = mock_delay_ms,
    };
    return &ops;
}
