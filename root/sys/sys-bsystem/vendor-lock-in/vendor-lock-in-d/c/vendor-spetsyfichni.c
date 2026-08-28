/* Діалект IAR C: ключові слова та прагми */
__ramfunc void Flash_EraseSector(uint32_t address);

#pragma location = 0x20000000
uint32_t SharedBuffer[256];

__packed struct TelemetryPacket {
    uint8_t  id;
    uint32_t timestamp;
};
