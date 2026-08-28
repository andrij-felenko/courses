#include <iostream>
#include <vector>

class SimulatedFlashHal : public FlashHal {
public:
    SimulatedFlashHal(size_t totalBytes) : memory_(totalBytes, 0xFF) {}

    bool read(uint32_t addr, std::span<uint8_t> dst) override {
        if (addr + dst.size() > memory_.size()) return false;
        std::copy_n(memory_.begin() + addr, dst.size(), dst.begin());
        return true;
    }

    bool write(uint32_t addr, std::span<const uint8_t> src) override {
        if (addr + src.size() > memory_.size()) return false;
        for (size_t i = 0; i < src.size(); ++i) {
            memory_[addr + i] &= src[i]; // Фізика переходу 1 -> 0
        }
        return true;
    }

    bool eraseSector(uint32_t sector_addr) override {
        uint32_t idx = sector_addr / PersistentRingLogger::SectorSize;
        if (idx >= PersistentRingLogger::SectorCount) return false;
        std::fill_n(memory_.begin() + (idx * PersistentRingLogger::SectorSize),
                    PersistentRingLogger::SectorSize, 0xFF);
        return true;
    }

private:
    std::vector<uint8_t> memory_;
};

int main() {
    SimulatedFlashHal hal(PersistentRingLogger::SectorSize * PersistentRingLogger::SectorCount);
    PersistentRingLogger logger(hal, 0);

    auto initRes = logger.init();
    if (!initRes) {
        return 1;
    }

    uint32_t v1 = 120;
    logger.log(LogLevel::Info, 1, 1000, 0x1001, std::as_bytes(std::span{&v1, 1}));
    uint32_t v2 = 404;
    logger.log(LogLevel::Warn, 2, 1050, 0x1002, std::as_bytes(std::span{&v2, 1}));

    // Перезапуск і перевірка стану
    PersistentRingLogger rebootedLogger(hal, 0);
    if (!rebootedLogger.init()) {
        return 1;
    }

    uint32_t v3 = 200;
    rebootedLogger.log(LogLevel::Info, 1, 1200, 0x1004, std::as_bytes(std::span{&v3, 1}));
    return 0;
}
