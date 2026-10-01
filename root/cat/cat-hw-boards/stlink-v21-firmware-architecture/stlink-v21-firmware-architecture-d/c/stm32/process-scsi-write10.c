// Опис обгортки SCSI CBW для перехоплення команд запису секторів
typedef struct {
    uint32_t signature;      // Сигнатура CBW ("USBC" або 0x43425355)
    uint32_t tag;            // Унікальний тег транзакції
    uint32_t data_length;    // Довжина даних передачі
    uint8_t  flags;          // Напрямок передачі (OUT = 0x00)
    uint8_t  lun;            // Логічний номер пристрою
    uint8_t  cb_length;      // Довжина SCSI-команди
    uint8_t  scsi_cmd[16];   // Масив SCSI-команди (0x2A відповідає WRITE_10)
} __attribute__((packed)) scsi_cbw_t;

void process_scsi_write10(uint32_t lba_sector, const uint8_t *data_buffer) {
    if (lba_sector >= VIRTUAL_FAT_DATA_START) {
        // Перехоплення сектора та прямий запис у флеш-пам'ять цільового STM32
        uint32_t flash_addr = TARGET_FLASH_BASE + (lba_sector - VIRTUAL_FAT_DATA_START) * 512;
        swd_write_flash_page(flash_addr, data_buffer, 512);
    }
}
