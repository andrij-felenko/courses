typedef struct {
    uint16_t input_ma;    /* скільки джерело дозволяє відібрати з входу */
    uint16_t charge_ma;   /* цільовий струм заряду */
    uint16_t charge_mv;   /* цільова напруга заряду, напр. 4200 */
    uint16_t term_ma;     /* поріг струму термінації */
} bq_cfg_t;

int bq_init(const bq_cfg_t *cfg)
{
    uint8_t id;

    /* 1. Хто на шині? PN у REG0A[5:3]: 100 = bq24190, 101 = bq24192. */
    if (bq_i2c_read(BQ_REG0A, &id)) return -1;
    uint8_t pn = (id >> 3) & 0x07;
    if (pn != 0x4 && pn != 0x5) return -2;         /* не той чип або битий зв'язок */

    /* 2. Скинути все у типовий стан (це вже запис → перехід у host mode). */
    if (bq_i2c_write(BQ_REG01, REG01_REG_RST)) return -3;
    bq_delay_ms(10);                                /* дати скиданню відпрацювати */

    /* 3. ЗАБОРОНИТИ заряд, поки не виставлені межі (CHG_CONFIG = 00). */
    if (bq_update(BQ_REG01, REG01_CHG_CONFIG_MASK, 0x00)) return -4;

    /* 4. ВХІДНИЙ ЛІМІТ — першим зі струмів: він оберігає джерело. */
    if (bq_update(BQ_REG00, REG00_IINLIM_MASK, iinlim_code(cfg->input_ma))) return -5;

    /* 5. Струм і напруга заряду, поріг термінації. */
    if (bq_update(BQ_REG02, REG02_ICHG_MASK,  ichg_reg(cfg->charge_ma)))  return -6;
    if (bq_update(BQ_REG04, REG04_VREG_MASK,  vreg_reg(cfg->charge_mv)))  return -7;
    if (bq_update(BQ_REG03, REG03_ITERM_MASK, iterm_code(cfg->term_ma)))  return -8;
    if (bq_update(BQ_REG05, REG05_EN_TERM, REG05_EN_TERM))                return -9;

    /* 6. ТЕПЕР дозволити заряд. */
    if (bq_update(BQ_REG01, REG01_CHG_CONFIG_MASK, REG01_CHG_ENABLE))     return -10;
    return 0;
}
