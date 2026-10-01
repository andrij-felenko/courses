struct ScsiWriteHandler {
    uint32_t dataStartSector;
    uint32_t currentAddress;

    void handleSectorWrite(uint32_t lba, const std::array<uint8_t, 512>& buffer) {
        if (lba >= dataStartSector) {
            // Трансляція даних сектора у SWD-команди програмування флеш-пам'яті
            swd_programmer::streamWriteTargetFlash(currentAddress, buffer.data(), buffer.size());
            currentAddress += buffer.size();
        } else {
            // Оновлення стану віртуального каталогу
            updateVirtualDirectory(buffer);
        }
    }
};
