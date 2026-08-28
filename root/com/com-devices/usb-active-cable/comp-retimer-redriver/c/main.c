#include <stdint.h>
#include <stdbool.h>

/* Регістри та бітові маски сигнального кондиціонера */
#define REG_CH_CTRL_BASE    0x10
#define REG_CTLE_CONFIG     0x14
#define REG_TX_DEEMPHASIS   0x18
#define REG_CDR_STATUS      0x20

#define CTLE_BOOST_MASK     0x0F
#define TX_SWING_MASK       0x07
#define CDR_LOCK_BIT        (1 << 7)

typedef struct {
    uint8_t i2c_addr;
    uint8_t channel_count;
    bool (*i2c_write)(uint8_t addr, uint8_t reg, uint8_t val);
    bool (*i2c_read)(uint8_t addr, uint8_t reg, uint8_t *val);
} retimer_dev_t;

/* Налаштування посилення CTLE (0..15 дБ) та деакцентуації Tx для обраного каналу */
bool retimer_configure_channel(const retimer_dev_t *dev, uint8_t ch, 
                               uint8_t ctle_boost_db, uint8_t deemph_db) {
    if (!dev || ch >= dev->channel_count) {
        return false;
    }
    if (ctle_boost_db > 15 || deemph_db > 7) {
        return false;
    }

    uint8_t ch_offset = ch * 0x10;
    uint8_t ctle_reg = REG_CTLE_CONFIG + ch_offset;
    uint8_t tx_reg = REG_TX_DEEMPHASIS + ch_offset;

    /* Запис коефіцієнта аналогового підсилення високих частот */
    if (!dev->i2c_write(dev->i2c_addr, ctle_reg, ctle_boost_db & CTLE_BOOST_MASK)) {
        return false;
    }

    /* Запис глибини деакцентуації вихідного каскаду для компенсації втрат */
    if (!dev->i2c_write(dev->i2c_addr, tx_reg, deemph_db & TX_SWING_MASK)) {
        return false;
    }

    return true;
}

/* Перевірка захоплення тактової частоти фазовим детектором CDR */
bool retimer_is_locked(const retimer_dev_t *dev, uint8_t ch) {
    if (!dev || ch >= dev->channel_count) {
        return false;
    }
    uint8_t status = 0;
    uint8_t reg = REG_CDR_STATUS + (ch * 0x10);
    if (!dev->i2c_read(dev->i2c_addr, reg, &status)) {
        return false;
    }
    return (status & CDR_LOCK_BIT) != 0;
}
