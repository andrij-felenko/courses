// Клас перехоплення SCSI-запитів для емуляції прошивача drag-and-drop
struct alignas(1) ScsiCbwHeader {
    uint32_t signature;
    uint32_t tag;
    uint32_t dataLength;
    uint8_t  flags;
    uint8_t  lun;
    uint8_t  commandLength;
    uint8_t  scsiCommand[16];

    bool isWrite10() const {
        return scsiCommand[0] == 0x2A; // SCSI opcode WRITE (10)
    }
};

void handleSectorWrite(uint32_t lba, const uint8_t* sectorBuffer) {
    if (lba >= VIRTUAL_FAT_DATA_START) {
        uint32_t targetAddress = TARGET_FLASH_BASE + (lba - VIRTUAL_FAT_DATA_START) * 512;
        SwdFlashEngine::writePage(targetAddress, sectorBuffer, 512);
    }
}
