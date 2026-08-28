/* Повертає ПОТОЧНИЙ стан фолтів (друге читання). */
int bq_read_fault(uint8_t *fault)
{
    uint8_t a, b;
    if (bq_i2c_read(BQ_REG09, &a)) return -1;   /* латч попереднього стану */
    if (bq_i2c_read(BQ_REG09, &b)) return -1;    /* справжній поточний стан */
    *fault = b;
    return 0;
}

/* Розбір поля CHRG_FAULT[5:4] */
const char *bq_chrg_fault_str(uint8_t fault)
{
    switch ((fault >> 4) & 0x03) {
        case 0: return "норма";
        case 1: return "вхідний фолт (OVP або поганий вхід)";
        case 2: return "теплове вимкнення";
        case 3: return "сплив запобіжний таймер";
    }
    return "?";
}
