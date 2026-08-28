#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define LMP91000_I2C_ADDR_7BIT        0x48

#define LMP91000_REG_STATUS           0x00
#define LMP91000_REG_LOCK             0x01
#define LMP91000_REG_TIACN            0x10
#define LMP91000_REG_REFCN            0x11
#define LMP91000_REG_MODECN           0x12

typedef enum {
    LMP91000_TIA_GAIN_EXT     = 0x00,
    LMP91000_TIA_GAIN_2K75    = 0x04,
    LMP91000_TIA_GAIN_3K5     = 0x08,
    LMP91000_TIA_GAIN_7K      = 0x0C,
    LMP91000_TIA_GAIN_14K     = 0x10,
    LMP91000_TIA_GAIN_35K     = 0x14,
    LMP91000_TIA_GAIN_120K    = 0x18,
    LMP91000_TIA_GAIN_350K    = 0x1C
} lmp91000_tia_gain_t;

typedef enum {
    LMP91000_RLOAD_10OHM      = 0x00,
    LMP91000_RLOAD_33OHM      = 0x01,
    LMP91000_RLOAD_50OHM      = 0x02,
    LMP91000_RLOAD_100OHM     = 0x03
} lmp91000_rload_t;

typedef enum {
    LMP91000_INT_ZERO_20PCT   = 0x00,
    LMP91000_INT_ZERO_50PCT   = 0x20,
    LMP91000_INT_ZERO_67PCT   = 0x40,
    LMP91000_INT_ZERO_BYPASS  = 0x60
} lmp91000_int_zero_t;

typedef enum {
    LMP91000_BIAS_SIGN_NEG    = 0x00,
    LMP91000_BIAS_SIGN_POS    = 0x10
} lmp91000_bias_sign_t;

typedef enum {
    LMP91000_BIAS_0PCT        = 0x00,
    LMP91000_BIAS_1PCT        = 0x01,
    LMP91000_BIAS_2PCT        = 0x02,
    LMP91000_BIAS_4PCT        = 0x03,
    LMP91000_BIAS_6PCT        = 0x04,
    LMP91000_BIAS_8PCT        = 0x05,
    LMP91000_BIAS_10PCT       = 0x06,
    LMP91000_BIAS_12PCT       = 0x07,
    LMP91000_BIAS_14PCT       = 0x08,
    LMP91000_BIAS_16PCT       = 0x09,
    LMP91000_BIAS_18PCT       = 0x0A,
    LMP91000_BIAS_20PCT       = 0x0B,
    LMP91000_BIAS_22PCT       = 0x0C,
    LMP91000_BIAS_24PCT       = 0x0D
} lmp91000_bias_mag_t;

typedef enum {
    LMP91000_OP_MODE_DEEP_SLEEP = 0x00,
    LMP91000_OP_MODE_2LEAD_GALV = 0x01,
    LMP91000_OP_MODE_STANDBY    = 0x02,
    LMP91000_OP_MODE_3LEAD_AMP  = 0x03,
    LMP91000_OP_MODE_TEMP_TIAON = 0x06,
    LMP91000_OP_MODE_TEMP_TIAOFF= 0x07
} lmp91000_op_mode_t;

typedef struct {
    lmp91000_tia_gain_t gain;
    lmp91000_rload_t rload;
    lmp91000_int_zero_t int_zero;
    lmp91000_bias_sign_t bias_sign;
    lmp91000_bias_mag_t bias_mag;
    float vref_volts;
    float sensitivity_na_per_ppm;
    float baseline_current_na;
} lmp91000_config_t;

typedef struct {
    lmp91000_config_t cfg;
    bool (*i2c_write)(uint8_t reg, uint8_t val);
    bool (*i2c_read)(uint8_t reg, uint8_t *val);
} lmp91000_t;

static float lmp91000_get_rtia_value(lmp91000_tia_gain_t gain) {
    switch (gain) {
        case LMP91000_TIA_GAIN_2K75:  return 2750.0f;
        case LMP91000_TIA_GAIN_3K5:   return 3500.0f;
        case LMP91000_TIA_GAIN_7K:    return 7000.0f;
        case LMP91000_TIA_GAIN_14K:   return 14000.0f;
        case LMP91000_TIA_GAIN_35K:   return 35000.0f;
        case LMP91000_TIA_GAIN_120K:  return 120000.0f;
        case LMP91000_TIA_GAIN_350K:  return 350000.0f;
        default:                      return 0.0f;
    }
}

static float lmp91000_get_zero_fraction(lmp91000_int_zero_t zero) {
    switch (zero) {
        case LMP91000_INT_ZERO_20PCT: return 0.20f;
        case LMP91000_INT_ZERO_50PCT: return 0.50f;
        case LMP91000_INT_ZERO_67PCT: return 0.67f;
        default:                      return 0.50f;
    }
}

bool lmp91000_init(lmp91000_t *dev, const lmp91000_config_t *cfg,
                   bool (*write_fn)(uint8_t, uint8_t),
                   bool (*read_fn)(uint8_t, uint8_t*)) {
    if (!dev || !cfg || !write_fn || !read_fn) return false;
    dev->cfg = *cfg;
    dev->i2c_write = write_fn;
    dev->i2c_read = read_fn;

    uint8_t status = 0;
    if (!dev->i2c_read(LMP91000_REG_STATUS, &status)) return false;

    if (!dev->i2c_write(LMP91000_REG_LOCK, 0x00)) return false;

    uint8_t tiacn = (uint8_t)dev->cfg.gain | (uint8_t)dev->cfg.rload;
    if (!dev->i2c_write(LMP91000_REG_TIACN, tiacn)) return false;

    uint8_t refcn = (uint8_t)dev->cfg.int_zero | (uint8_t)dev->cfg.bias_sign | (uint8_t)dev->cfg.bias_mag;
    if (!dev->i2c_write(LMP91000_REG_REFCN, refcn)) return false;

    if (!dev->i2c_write(LMP91000_REG_LOCK, 0x01)) return false;

    uint8_t modecn = (uint8_t)LMP91000_OP_MODE_3LEAD_AMP;
    return dev->i2c_write(LMP91000_REG_MODECN, modecn);
}

bool lmp91000_set_mode(lmp91000_t *dev, lmp91000_op_mode_t mode, bool shorting_fet_en) {
    if (!dev || !dev->i2c_write) return false;
    uint8_t modecn = (uint8_t)mode;
    if (shorting_fet_en) {
        modecn |= 0x80;
    }
    return dev->i2c_write(LMP91000_REG_MODECN, modecn);
}

float lmp91000_voltage_to_current_na(const lmp91000_t *dev, float vout_volts) {
    if (!dev) return 0.0f;
    float rtia = lmp91000_get_rtia_value(dev->cfg.gain);
    if (rtia <= 0.0f) return 0.0f;

    float v_zero = dev->cfg.vref_volts * lmp91000_get_zero_fraction(dev->cfg.int_zero);
    float delta_v = vout_volts - v_zero;

    float current_amps = delta_v / rtia;
    return current_amps * 1.0e9f;
}

float lmp91000_calculate_ppm(const lmp91000_t *dev, float vout_volts, float temperature_c) {
    if (!dev || dev->cfg.sensitivity_na_per_ppm <= 0.0f) return 0.0f;

    float current_na = lmp91000_voltage_to_current_na(dev, vout_volts);

    float temp_drift_factor = 1.0f + 0.003f * (temperature_c - 20.0f);
    float baseline_t = dev->cfg.baseline_current_na * temp_drift_factor;

    float net_gas_current_na = current_na - baseline_t;
    if (net_gas_current_na < 0.0f) {
        net_gas_current_na = 0.0f;
    }

    float sensitivity_t = dev->cfg.sensitivity_na_per_ppm * temp_drift_factor;
    return net_gas_current_na / sensitivity_t;
}

float lmp91000_raw_voltage_to_temperature(float vout_volts) {
    const float v_at_0c = 1.632f;
    const float tc_volts_per_deg = -0.0082f;
    return (vout_volts - v_at_0c) / tc_volts_per_deg;
}
