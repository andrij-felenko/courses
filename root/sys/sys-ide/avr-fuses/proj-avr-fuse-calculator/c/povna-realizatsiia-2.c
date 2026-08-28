int main(int argc, char* argv[]) {
    avr_human_config_t config = {
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
        .boot_lock_boot_bits = 0x03
    };

    const char* target_chip = "m328p";
    bool output_json = false;
    bool allow_hvpp = false;

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--chip") == 0 && i + 1 < argc) {
            target_chip = argv[++i];
        } else if (strcmp(argv[i], "--clock") == 0 && i + 1 < argc) {
            const char* clk = argv[++i];
            if (strcmp(clk, "int-8mhz") == 0) config.clock_source = CLK_INT_RC_8MHZ;
            else if (strcmp(clk, "ext-clock") == 0) config.clock_source = CLK_EXT_CLOCK;
            else if (strcmp(clk, "int-128k") == 0) config.clock_source = CLK_INT_128KHZ;
            else config.clock_source = CLK_EXT_CRYSTAL_HIGH;
        } else if (strcmp(argv[i], "--div8") == 0) {
            config.divide_clock_by_8 = true;
        } else if (strcmp(argv[i], "--bod") == 0 && i + 1 < argc) {
            const char* b = argv[++i];
            if (strcmp(b, "disabled") == 0) config.bod_level = BOD_DISABLED;
            else if (strcmp(b, "1.8v") == 0) config.bod_level = BOD_1V8;
            else if (strcmp(b, "4.3v") == 0) config.bod_level = BOD_4V3;
            else config.bod_level = BOD_2V7;
        } else if (strcmp(argv[i], "--allow-hvpp") == 0) {
            allow_hvpp = true;
        } else if (strcmp(argv[i], "--json") == 0) {
            output_json = true;
        }
    }

    avr_raw_fuses_t raw = avr_encode_fuses(&config);
    avr_audit_result_t audit = avr_validate_fuses(raw, allow_hvpp);

    if (output_json) {
        printf("{\n");
        printf("  \"chip\": \"%s\",\n", target_chip);
        printf("  \"lfuse\": \"0x%02X\",\n", raw.lfuse);
        printf("  \"hfuse\": \"0x%02X\",\n", raw.hfuse);
        printf("  \"efuse\": \"0x%02X\",\n", raw.efuse);
        printf("  \"lock\": \"0x%02X\",\n", raw.lock);
        printf("  \"is_safe\": %s,\n", audit.is_valid_and_safe ? "true" : "false");
        printf("  \"issues\": [\n");
        for (size_t i = 0; i < audit.count; ++i) {
            printf("    {\"level\": %d, \"message\": \"%s\"}%s\n",
                   audit.items[i].level, audit.items[i].message,
                   (i + 1 < audit.count) ? "," : "");
        }
        printf("  ]\n");
        printf("}\n");
    } else {
        printf("=== Результати розрахунку фьюзів для %s ===\n", target_chip);
        printf(" Low Fuse (lfuse)     : 0x%02X\n", raw.lfuse);
        printf(" High Fuse (hfuse)    : 0x%02X\n", raw.hfuse);
        printf(" Ext Fuse (efuse)     : 0x%02X\n", raw.efuse);
        printf(" Lock Bits (lock)     : 0x%02X\n\n", raw.lock);

        char cmd[256];
        avr_format_avrdude_cmd(cmd, sizeof(cmd), target_chip, raw);
        printf("Команда для AVRDUDE:\n  %s\n\n", cmd);

        printf("Статус аудиту безпеки: %s\n", audit.is_valid_and_safe ? "БЕЗПЕЧНО" : "ВИЯВЛЕНО ФАТАЛЬНІ ПОМИЛКИ");
        for (size_t i = 0; i < audit.count; ++i) {
            const char* tag = (audit.items[i].level == DIAG_CRITICAL_ERROR) ? "[ФАТАЛЬНО]" :
                              (audit.items[i].level == DIAG_WARNING) ? "[ПОПЕРЕДЖЕННЯ]" : "[ІНФО]";
            printf(" %s %s\n", tag, audit.items[i].message);
        }
    }

    return audit.is_valid_and_safe ? EXIT_SUCCESS : EXIT_FAILURE;
}
