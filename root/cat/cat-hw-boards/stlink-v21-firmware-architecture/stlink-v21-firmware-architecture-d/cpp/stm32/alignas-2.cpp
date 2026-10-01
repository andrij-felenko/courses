// Клас керування запитом переходу в режим оновлення DFU
struct alignas(1) StlinkDfuRequest {
    uint8_t  cmdGroup;      // Група команд DFU
    uint8_t  subCmd;        // Підкоманда DFU
    uint16_t magicKey;      // Ключ авторизації
    uint8_t  padding[12];   // Заповнення буфера

    static StlinkDfuRequest makeDfuEntry() {
        return {0xF3, 0x07, 0x55AA, {0}};
    }
};

void triggerBootloaderReset(const StlinkDfuRequest& req) {
    if (req.magicKey == 0x55AA) {
        *reinterpret_cast<volatile uint32_t*>(BACKUP_RAM_MAGIC_ADDR) = DFU_BOOT_MAGIC_VALUE;
        NVIC_SystemReset();
    }
}
