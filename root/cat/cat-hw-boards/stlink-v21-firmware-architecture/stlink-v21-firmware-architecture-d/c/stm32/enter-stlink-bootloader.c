// Формат пакета для переходу прошивки ST-Link V2.1 у режим DFU
typedef struct {
    uint8_t  dfu_cmd;        // Група команд DFU (0xF3)
    uint8_t  sub_cmd;        // Підкоманда переходу (0x07)
    uint16_t magic_key;      // Авторизаційний ключ переходу (0x55AA)
    uint8_t  reserved[12];   // Резервний падинг буфера Bulk OUT
} __attribute__((packed)) stlink_dfu_entry_t;

void enter_stlink_bootloader(const stlink_dfu_entry_t *cmd) {
    if (cmd->magic_key == 0x55AA) {
        // Установка прапора в пам'яті та перезапуск мікроконтролера
        *(__IO uint32_t *)BACKUP_RAM_MAGIC_ADDR = DFU_BOOT_MAGIC_VALUE;
        NVIC_SystemReset();
    }
}
