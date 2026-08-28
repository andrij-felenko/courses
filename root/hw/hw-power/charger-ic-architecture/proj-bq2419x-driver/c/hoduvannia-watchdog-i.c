int bq_watchdog_kick(void)
{
    uint8_t r;
    if (bq_i2c_read(BQ_REG01, &r)) return -1;
    r |= REG01_WD_RST;                    /* біт 6, самоскидний */
    /* Даташит просить писати одиницю двічі — пишемо двічі поспіль. */
    if (bq_i2c_write(BQ_REG01, r)) return -1;
    if (bq_i2c_write(BQ_REG01, r)) return -1;
    return 0;
}
