/* Перевірка ревізії кремнію та вибір обхідного шляху (C) */
#define REG_REVISION_ID     0x0C
#define SILICON_REV_A       0x01
#define SILICON_REV_B       0x02

void sensor_probe_workaround(uint8_t dev_addr) {
    uint8_t rev_id = 0;
    i2c_read_byte(dev_addr, REG_REVISION_ID, &rev_id);

    if (rev_id == SILICON_REV_A) {
        /* Активуємо спеціальний обхідний шлях для дефектної ревізії А */
        apply_errata_workaround_es042();
    }
}
