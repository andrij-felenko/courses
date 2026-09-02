#include "sx126x_rf.h"

#include <string.h>

/* Коди команд SX1261/1262/1268 (даташит, розділ 13). */
#define SX126X_CMD_READ_REGISTER     0x1Du
#define SX126X_CMD_CLR_IRQ_STATUS    0x02u
#define SX126X_CMD_GET_IRQ_STATUS    0x12u
#define SX126X_CMD_GET_PACKET_STATUS 0x14u
#define SX126X_CMD_GET_RSSI_INST     0x15u

/* Регістр режиму вхідного підсилення: 0x94 — економний, 0x96 — boosted. */
#define SX126X_REG_RX_GAIN           0x08ACu
#define SX126X_RX_GAIN_POWER_SAVING  0x94u

/* Прапорці IRQ. */
#define SX126X_IRQ_RX_DONE           (1u << 1)
#define SX126X_IRQ_PREAMBLE_DETECTED (1u << 2)
#define SX126X_IRQ_SYNC_WORD_VALID   (1u << 3)
#define SX126X_IRQ_HEADER_ERR        (1u << 5)
#define SX126X_IRQ_CRC_ERR           (1u << 6)
#define SX126X_IRQ_ALL               0xFFFFu

#define SX126X_BUSY_TIMEOUT_US       (1000u)

/* Демодулятор LoRa бере кадр аж до -20 дБ SNR. Якщо кадру не було зовсім,
   фактичне відношення сигнал/шум лежить нижче цієї межі — саме це число і
   чесно віддаємо класифікаторові замість нуля. */
#define SX126X_SNR_BELOW_FLOOR_DB    (-20)

static sx126x_status_t sx126x_cmd(const uint8_t *tx, uint8_t *rx, size_t len)
{
    if (!sx126x_bsp_wait_busy(SX126X_BUSY_TIMEOUT_US)) {
        return SX126X_ERR_BUSY;
    }
    if (!sx126x_bsp_xfer(tx, rx, len)) {
        return SX126X_ERR_SPI;
    }
    return SX126X_OK;
}

static sx126x_status_t sx126x_get_irq(uint16_t *irq)
{
    /* [опкод][статус][IRQ старший][IRQ молодший] */
    uint8_t tx[4] = { SX126X_CMD_GET_IRQ_STATUS, 0, 0, 0 };
    uint8_t rx[4] = { 0 };

    const sx126x_status_t st = sx126x_cmd(tx, rx, sizeof(tx));
    if (st != SX126X_OK) {
        return st;
    }
    *irq = (uint16_t)(((uint16_t)rx[2] << 8) | rx[3]);
    return SX126X_OK;
}

static sx126x_status_t sx126x_clear_irq(uint16_t mask)
{
    uint8_t tx[3] = { SX126X_CMD_CLR_IRQ_STATUS, (uint8_t)(mask >> 8), (uint8_t)mask };
    uint8_t rx[3] = { 0 };
    return sx126x_cmd(tx, rx, sizeof(tx));
}

static sx126x_status_t sx126x_get_rssi_inst(int16_t *rssi_dbm)
{
    uint8_t tx[3] = { SX126X_CMD_GET_RSSI_INST, 0, 0 };
    uint8_t rx[3] = { 0 };

    const sx126x_status_t st = sx126x_cmd(tx, rx, sizeof(tx));
    if (st != SX126X_OK) {
        return st;
    }
    /* RSSI_дБм = -rssi_raw / 2 */
    *rssi_dbm = (int16_t)(-((int16_t)rx[2]) / 2);
    return SX126X_OK;
}

static sx126x_status_t sx126x_get_packet_snr(int8_t *snr_db)
{
    /* [опкод][статус][RssiPkt][SnrPkt][SignalRssiPkt] */
    uint8_t tx[5] = { SX126X_CMD_GET_PACKET_STATUS, 0, 0, 0, 0 };
    uint8_t rx[5] = { 0 };

    const sx126x_status_t st = sx126x_cmd(tx, rx, sizeof(tx));
    if (st != SX126X_OK) {
        return st;
    }
    /* SnrPkt — знакове, у чвертях дБ. */
    *snr_db = (int8_t)((int8_t)rx[3] / 4);
    return SX126X_OK;
}

static sx126x_status_t sx126x_read_reg(uint16_t addr, uint8_t *value)
{
    /* [опкод][адреса старша][адреса молодша][NOP][дані] */
    uint8_t tx[5] = { SX126X_CMD_READ_REGISTER, (uint8_t)(addr >> 8), (uint8_t)addr, 0, 0 };
    uint8_t rx[5] = { 0 };

    const sx126x_status_t st = sx126x_cmd(tx, rx, sizeof(tx));
    if (st != SX126X_OK) {
        return st;
    }
    *value = rx[4];
    return SX126X_OK;
}

/* SX126x не публікує крок AGC жодним регістром, тож відновлюємо його з робочої
   точки: чим сильніший вхід, тим нижче тракт мусив опустити підсилення.
   -120 дБм → 255 (максимум LNA), -20 дБм → 0 (вхід у насиченні). */
static uint8_t sx126x_agc_code(int16_t rssi_dbm, uint8_t rx_gain_reg)
{
    int32_t code = 255 - (((int32_t)rssi_dbm + 120) * 255) / 100;
    if (code < 0) {
        code = 0;
    }
    if (code > 255) {
        code = 255;
    }
    /* В економному режимі тракт уже віддав частину підсилення. */
    if (rx_gain_reg == SX126X_RX_GAIN_POWER_SAVING) {
        code = (code > 20) ? code - 20 : 0;
    }
    return (uint8_t)code;
}

sx126x_status_t sx126x_read_sample(ew_rf_sample_t *out)
{
    if (!out) {
        return SX126X_ERR_ARG;
    }

    uint16_t irq = 0;
    sx126x_status_t st = sx126x_get_irq(&irq);
    if (st != SX126X_OK) {
        return st;
    }

    memset(out, 0, sizeof(*out));
    out->timestamp_ms = sx126x_bsp_now_ms();

    /* Беремо саме миттєвий RSSI, а не рівень пакета: він міряє ефір, зокрема
       й тоді, коли пакетів немає взагалі — а це і є картина глушіння. */
    st = sx126x_get_rssi_inst(&out->rssi_dbm);
    if (st != SX126X_OK) {
        return st;
    }

    out->preamble_detected = (irq & (SX126X_IRQ_PREAMBLE_DETECTED | SX126X_IRQ_SYNC_WORD_VALID)) != 0u;
    out->crc_error = (irq & (SX126X_IRQ_CRC_ERR | SX126X_IRQ_HEADER_ERR)) != 0u;

    const bool had_frame = (irq & (SX126X_IRQ_RX_DONE | SX126X_IRQ_CRC_ERR | SX126X_IRQ_HEADER_ERR)) != 0u;
    if (had_frame) {
        st = sx126x_get_packet_snr(&out->snr_db);
        if (st != SX126X_OK) {
            return st;
        }
    } else {
        out->snr_db = SX126X_SNR_BELOW_FLOOR_DB;
    }

    uint8_t rx_gain = 0;
    st = sx126x_read_reg(SX126X_REG_RX_GAIN, &rx_gain);
    if (st != SX126X_OK) {
        return st;
    }
    out->agc_gain_code = sx126x_agc_code(out->rssi_dbm, rx_gain);

    /* Прапорці треба гасити самому: інакше один-єдиний CRC-збій висітиме в
       регістрі вічно, і вікно назавжди лишиться «побитим». */
    return sx126x_clear_irq(SX126X_IRQ_ALL);
}
