void run_unit_tests(void) {
    printf("=== Запуск модульних тестів калькулятора фьюзів (C99) ===\n");
    
    // Тест 1: Заводський профіль ATmega328P
    avr_human_config_t cfg_factory = {
        .clock_source        = CLK_INT_RC_8MHZ,
        .startup_time        = SUT_MAX_CERAMIC,
        .divide_clock_by_8   = true,
        .clock_output_enable = false,
        .reset_disable       = false,
        .debugwire_enable    = false,
        .spi_prog_enable     = true,
        .watchdog_always_on  = false,
        .preserve_eeprom     = false,
        .bootloader_size     = BOOT_SIZE_2048_WORDS,
        .boot_reset_vector   = false,
        .bod_level           = BOD_DISABLED,
        .lock_mode           = LOCK_MODE_1_OPEN,
        .boot_lock_app_bits  = 0x03,
        .boot_lock_boot_bits = 0x03
    };
    
    avr_raw_fuses_t raw_factory = avr_encode_fuses(&cfg_factory);
    printf("Заводський профіль: LFUSE=0x%02X (очікується 0x62), HFUSE=0x%02X (очікується 0xD9), EFUSE=0x%02X (очікується 0xFF)\n",
           raw_factory.lfuse, raw_factory.hfuse, raw_factory.efuse);
           
    if (raw_factory.lfuse == 0x62 && raw_factory.hfuse == 0xD9 && raw_factory.efuse == 0xFF) {
        printf(" [PASS] Тест заводського профілю пройдено успішно.\n");
    } else {
        printf(" [FAIL] Помилка кодування заводського профілю!\n");
    }
    
    // Тест 2: Профіль Arduino Uno
    avr_human_config_t cfg_uno = {
        .clock_source        = CLK_EXT_CRYSTAL_HIGH,
        .startup_time        = SUT_MAX_CERAMIC,
        .divide_clock_by_8   = false,
        .clock_output_enable = false,
        .reset_disable       = false,
        .debugwire_enable    = false,
        .spi_prog_enable     = true,
        .watchdog_always_on  = false,
        .preserve_eeprom     = false,
        .bootloader_size     = BOOT_SIZE_256_WORDS,
        .boot_reset_vector   = true,
        .bod_level           = BOD_2V7,
        .lock_mode           = LOCK_MODE_1_OPEN,
        .boot_lock_app_bits  = 0x03,
        .boot_lock_boot_bits = 0x00 // Захист Optiboot
    };
    
    avr_raw_fuses_t raw_uno = avr_encode_fuses(&cfg_uno);
    printf("Профіль Arduino Uno: LFUSE=0x%02X (очікується 0xFF), HFUSE=0x%02X (очікується 0xDE), EFUSE=0x%02X (очікується 0xFD)\n",
           raw_uno.lfuse, raw_uno.hfuse, raw_uno.efuse);
           
    if (raw_uno.lfuse == 0xFF && raw_uno.hfuse == 0xDE && (raw_uno.efuse & 0x07) == 0x05) {
        printf(" [PASS] Тест профілю Arduino Uno пройдено успішно.\n");
    } else {
        printf(" [FAIL] Помилка кодування профілю Arduino Uno!\n");
    }
}
