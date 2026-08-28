void compass_begin() {
    Wire.begin();

    if (i2c_present(ADDR_HMC)) {
        chip = CHIP_HMC;
        // Config A (0x00): 8 усереднень, 15 Гц, нормальний вимір
        reg_write(ADDR_HMC, 0x00, 0x70);
        // Config B (0x01): підсилення ±1.3 Гаус (1090 LSB/Гаус)
        reg_write(ADDR_HMC, 0x01, 0x20);
        // Mode (0x02): безперервний вимір
        reg_write(ADDR_HMC, 0x02, 0x00);
    }
    else if (i2c_present(ADDR_QMC)) {
        chip = CHIP_QMC;
        // М'яке скидання — почати з чистого стану
        reg_write(ADDR_QMC, 0x0A, 0x80);
        delay(5);
        // SET/RESET Period (0x0B): рекомендоване datasheet значення 0x01.
        // БЕЗ цього кроку QMC віддає нестабільне сміття!
        reg_write(ADDR_QMC, 0x0B, 0x01);
        // Control 1 (0x09): OSR=512 | RNG=±2Гаус | ODR=200Гц | безперервний
        // 0x00 | 0x00 | 0x0C | 0x01 = 0x1D
        reg_write(ADDR_QMC, 0x09, 0x1D);
    }
    else {
        chip = CHIP_NONE;   // нічого не знайдено
    }
}
