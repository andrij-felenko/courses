typedef struct {
    uint8_t opcode;        // 0x2A = SCSI WRITE (10)
    uint8_t flags;
    uint32_t lba;          // Logical Block Address (номер сектора)
    uint16_t transfer_len; // Кількість секторів для запису
    uint8_t control;
} __attribute__((packed)) scsi_write10_cbw_t;

void process_scsi_write(const scsi_write10_cbw_t *cmd, const uint8_t *sector_data) {
    uint32_t sector_offset = cmd->lba * FAT_SECTOR_SIZE;

    // Перевіряємо, чи припадає сектор на область даних файлової системи
    if (cmd->lba >= fat_layout.data_start_sector) {
        if (current_stream_state.is_intel_hex) {
            parse_intel_hex_chunk(sector_data, FAT_SECTOR_SIZE);
        } else {
            // Прямий потоковий запис бінарного масиву у флеш цільового мікроконтролера
            swd_flash_write_block(current_target_address, sector_data, FAT_SECTOR_SIZE);
            current_target_address += FAT_SECTOR_SIZE;
        }
    } else if (cmd->lba == fat_layout.root_dir_sector) {
        // Парсинг запису каталогу для визначення імені та розширення файлу (.BIN / .HEX)
        inspect_directory_entry((const fat_dir_entry_t *)sector_data);
    }
}
