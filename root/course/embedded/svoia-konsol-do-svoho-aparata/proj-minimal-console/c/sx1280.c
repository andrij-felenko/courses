#include "sx1280.h"

#include <string.h>

#include "hal.h"

#define BUSY_TIMEOUT_US 2000

// Обмін іде через ці два буфери: вони у DMA-придатній пам'яті й вирівняні.
// Контекст один (задача реального часу), тож статика тут безпечна.
static HAL_DMA_ATTR uint8_t s_tx[24];
static HAL_DMA_ATTR uint8_t s_rx[24];
static int8_t s_last_rssi = -127;

// BUSY піднімається на час виконання команди; поки він високий, чип нову
// транзакцію просто проковтне мовчки.
static bool wait_busy(void)
{
    uint32_t t0 = hal_micros();
    while (hal_gpio_read(PIN_RADIO_BUSY)) {
        if (hal_micros() - t0 > BUSY_TIMEOUT_US) {
            return false;
        }
    }
    return true;
}

static bool xfer(size_t len, bool need_rx)
{
    if (!wait_busy()) {
        return false;
    }
    hal_cache_writeback(s_tx, len);
    hal_gpio_write(PIN_RADIO_NSS, false);
    hal_spi_xfer(s_tx, need_rx ? s_rx : NULL, len);
    hal_gpio_write(PIN_RADIO_NSS, true);
    if (need_rx) {
        // Дані поклав DMA — рядки кешу під s_rx застарілі.
        hal_cache_invalidate(s_rx, len);
    }
    return true;
}

static bool cmd(uint8_t opcode, const uint8_t *params, size_t n)
{
    if (n + 1 > sizeof s_tx) {
        return false;
    }
    s_tx[0] = opcode;
    if (n) {
        memcpy(&s_tx[1], params, n);
    }
    return xfer(n + 1, false);
}

// Читання: опкод, один NOP-байт (у ньому чип віддає статус), далі дані.
static bool cmd_get(uint8_t opcode, uint8_t *out, size_t n)
{
    if (n + 2 > sizeof s_tx) {
        return false;
    }
    memset(s_tx, 0, n + 2);
    s_tx[0] = opcode;
    if (!xfer(n + 2, true)) {
        return false;
    }
    memcpy(out, &s_rx[2], n);
    return true;
}

static bool write_register(uint16_t addr, const uint8_t *data, size_t n)
{
    if (n + 3 > sizeof s_tx) {
        return false;
    }
    s_tx[0] = SX1280_CMD_WRITE_REGISTER;
    s_tx[1] = (uint8_t)(addr >> 8);
    s_tx[2] = (uint8_t)(addr & 0xFF);
    memcpy(&s_tx[3], data, n);
    return xfer(n + 3, false);
}

void sx1280_reset(void)
{
    hal_gpio_write(PIN_RADIO_NSS, true);
    hal_gpio_write(PIN_RADIO_RESET, false);
    hal_delay_us(200);
    hal_gpio_write(PIN_RADIO_RESET, true);
    hal_delay_us(3000);   // чипу треба близько 2.5 мс на внутрішній старт
}

bool sx1280_status(uint8_t *status)
{
    s_tx[0] = SX1280_CMD_GET_STATUS;
    s_tx[1] = 0x00;
    if (!xfer(2, true)) {
        return false;
    }
    *status = s_rx[1];
    return true;
}

bool sx1280_init(uint8_t payload_len)
{
    sx1280_reset();

    uint8_t status = 0;
    if (!sx1280_status(&status)) {
        return false;
    }
    // Поле CircuitMode: 0 і 7 означають, що на шині або тиша, або суцільні 0xFF.
    uint8_t mode = (uint8_t)((status >> 5) & 0x07);
    if (mode == 0x00 || mode == 0x07) {
        return false;
    }

    uint8_t p[8];

    p[0] = SX1280_STDBY_RC;
    if (!cmd(SX1280_CMD_SET_STANDBY, p, 1)) {
        return false;
    }
    p[0] = 0x01;   // DC-DC: на платі пульта під нього стоїть дросель 15 мкГн
    if (!cmd(SX1280_CMD_SET_REGULATOR_MODE, p, 1)) {
        return false;
    }
    p[0] = SX1280_PACKET_TYPE_FLRC;
    if (!cmd(SX1280_CMD_SET_PACKET_TYPE, p, 1)) {
        return false;
    }

    // Крок сітки частот — XTAL/2^18 ≈ 198.36 Гц; ділимо в 64 бітах, щоб не
    // втратити молодші розряди.
    uint32_t pll = (uint32_t)(((uint64_t)SX1280_RF_HZ << 18) / 52000000u);
    p[0] = (uint8_t)(pll >> 16);
    p[1] = (uint8_t)(pll >> 8);
    p[2] = (uint8_t)pll;
    if (!cmd(SX1280_CMD_SET_RF_FREQUENCY, p, 3)) {
        return false;
    }

    p[0] = 0x00;   // база буфера передавання
    p[1] = 0x00;   // база буфера приймання
    if (!cmd(SX1280_CMD_SET_BUFFER_BASE, p, 2)) {
        return false;
    }

    p[0] = SX1280_FLRC_BR_1_300_BW_1_2;
    p[1] = SX1280_FLRC_CR_3_4;
    p[2] = SX1280_FLRC_BT_0_5;
    if (!cmd(SX1280_CMD_SET_MOD_PARAMS, p, 3)) {
        return false;
    }

    static const uint8_t sync[4] = {0x54, 0x69, 0x96, 0x1E};
    if (!write_register(SX1280_REG_FLRC_SYNC_WORD1, sync, sizeof sync)) {
        return false;
    }

    p[0] = SX1280_PREAMBLE_32_BITS;
    p[1] = SX1280_FLRC_SYNC_LEN_4B;
    p[2] = SX1280_RX_MATCH_SYNC_1;
    p[3] = SX1280_PACKET_FIXED_LEN;   // довжина кадру відома обом сторонам
    p[4] = payload_len;
    p[5] = SX1280_CRC_OFF;            // свій CRC-16 уже в кадрі — не платимо двічі
    p[6] = SX1280_WHITENING_OFF;      // для FLRC вибілювання має бути вимкнене
    if (!cmd(SX1280_CMD_SET_PACKET_PARAMS, p, 7)) {
        return false;
    }

    p[0] = 0x1F;   // +13 dBm на виході чипа, до +20 dBm дотягує зовнішній PA
    p[1] = SX1280_RAMP_20_US;
    if (!cmd(SX1280_CMD_SET_TX_PARAMS, p, 2)) {
        return false;
    }

    uint16_t mask = SX1280_IRQ_TX_DONE | SX1280_IRQ_RX_DONE |
                    SX1280_IRQ_CRC_ERROR | SX1280_IRQ_RX_TX_TIMEOUT;
    p[0] = (uint8_t)(mask >> 8);
    p[1] = (uint8_t)mask;          // загальна маска переривань
    p[2] = (uint8_t)(mask >> 8);
    p[3] = (uint8_t)mask;          // та сама маска виведена на DIO1
    p[4] = 0x00;
    p[5] = 0x00;
    p[6] = 0x00;
    p[7] = 0x00;
    if (!cmd(SX1280_CMD_SET_DIO_IRQ_PARAMS, p, 8)) {
        return false;
    }

    return sx1280_clear_irq(0xFFFF);
}

bool sx1280_transmit(const uint8_t *payload, size_t len)
{
    if (len + 2 > sizeof s_tx) {
        return false;
    }
    if (!sx1280_clear_irq(0xFFFF)) {
        return false;
    }
    s_tx[0] = SX1280_CMD_WRITE_BUFFER;
    s_tx[1] = 0x00;
    memcpy(&s_tx[2], payload, len);
    if (!xfer(len + 2, false)) {
        return false;
    }
    // Апаратний таймаут 3 мс: якщо передача не завершиться, чип сам вийде
    // в STDBY і не залишить PA ввімкненим.
    uint8_t p[3] = {SX1280_PERIOD_BASE_1MS, 0x00, 0x03};
    return cmd(SX1280_CMD_SET_TX, p, 3);
}

bool sx1280_listen(uint32_t window_us)
{
    if (!sx1280_clear_irq(0xFFFF)) {
        return false;
    }
    uint32_t ticks = (window_us * 64u) / 1000u;   // 1 такт = 15.625 мкс
    if (ticks > 0xFFFFu) {
        ticks = 0xFFFFu;
    }
    uint8_t p[3] = {SX1280_PERIOD_BASE_15US, (uint8_t)(ticks >> 8), (uint8_t)ticks};
    return cmd(SX1280_CMD_SET_RX, p, 3);
}

bool sx1280_irq_status(uint16_t *out)
{
    uint8_t b[2];
    if (!cmd_get(SX1280_CMD_GET_IRQ_STATUS, b, sizeof b)) {
        return false;
    }
    *out = (uint16_t)(((uint16_t)b[0] << 8) | b[1]);
    return true;
}

bool sx1280_clear_irq(uint16_t mask)
{
    uint8_t p[2] = {(uint8_t)(mask >> 8), (uint8_t)mask};
    return cmd(SX1280_CMD_CLR_IRQ_STATUS, p, sizeof p);
}

bool sx1280_wait_irq(uint16_t mask, uint32_t timeout_us, uint16_t *out_irq)
{
    uint32_t t0 = hal_micros();
    for (;;) {
        // Спершу дивимося на лінію DIO1 — читати регістр щоразу означало б
        // тримати шину зайнятою і красти в дисплея його вікно.
        if (hal_gpio_read(PIN_RADIO_DIO1)) {
            uint16_t irq = 0;
            if (!sx1280_irq_status(&irq)) {
                return false;
            }
            if (irq & mask) {
                if (out_irq) {
                    *out_irq = irq;
                }
                sx1280_clear_irq(irq);
                return true;
            }
        }
        if (hal_micros() - t0 > timeout_us) {
            return false;
        }
    }
}

size_t sx1280_read_packet(uint8_t *out, size_t max)
{
    uint8_t st[2];
    if (!cmd_get(SX1280_CMD_GET_RX_BUF_STATUS, st, sizeof st)) {
        return 0;
    }
    size_t len = st[0];
    uint8_t offset = st[1];
    if (len == 0 || len > max || len + 3 > sizeof s_tx) {
        return 0;
    }

    memset(s_tx, 0, len + 3);
    s_tx[0] = SX1280_CMD_READ_BUFFER;
    s_tx[1] = offset;
    // Третій такт — NOP: дані з буфера чипа йдуть починаючи з нього.
    if (!xfer(len + 3, true)) {
        return 0;
    }
    memcpy(out, &s_rx[3], len);

    // RSSI беремо одразу: наступний прийом перепише статус пакета.
    uint8_t ps[5];
    if (cmd_get(SX1280_CMD_GET_PACKET_STATUS, ps, sizeof ps)) {
        s_last_rssi = (int8_t)(-(int)(ps[0] / 2));
    }
    return len;
}

int8_t sx1280_last_rssi(void)
{
    return s_last_rssi;
}

bool sx1280_standby(void)
{
    uint8_t p = SX1280_STDBY_RC;
    return cmd(SX1280_CMD_SET_STANDBY, &p, 1);
}
