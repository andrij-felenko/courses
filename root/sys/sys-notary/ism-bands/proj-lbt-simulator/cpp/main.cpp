#include <iostream>
#include <cstdint>
#include <chrono>
#include <vector>

class IsmTransmissionController {
public:
    static constexpr uint32_t DutyCycleLimitMs = 36000;   // 1% на годину (36 000 мс)
    static constexpr uint32_t WindowOneHourMs   = 3600000; // 3 600 000 мс
    static constexpr int16_t  RssiThresholdDbm   = -85;     // дБм
    static constexpr uint8_t  LbtSampleCount     = 5;

    explicit IsmTransmissionController(uint32_t startTimeMs = 0)
        : totalTxTimeMs_(0), windowStartMs_(startTimeMs) {}

    bool canTransmit(uint32_t currentTimeMs, uint32_t packetToaMs) {
        updateWindow(currentTimeMs);
        return (totalTxTimeMs_ + packetToaMs) <= DutyCycleLimitMs;
    }

    bool transmitPacket(uint32_t currentTimeMs, uint32_t packetToaMs) {
        if (!canTransmit(currentTimeMs, packetToaMs)) {
            std::cout << "[ISM Error] Перевищено ліміт Duty Cycle (1%)! Передачу блоковано.\n";
            return false;
        }

        if (!isChannelClear()) {
            std::cout << "[ISM Warning] Канал зайнятий (LBT fail). Застосовуємо backoff.\n";
            return false;
        }

        std::cout << "[ISM Tx] Канал чистий. Передача пакета тривалістю " << packetToaMs << " мс...\n";
        totalTxTimeMs_ += packetToaMs;
        std::cout << "[ISM Status] Витрачено бюджету: " << totalTxTimeMs_
                  << " / " << DutyCycleLimitMs << " мс на годину.\n";
        return true;
    }

    [[nodiscard]] uint32_t getRemainingBudgetMs(uint32_t currentTimeMs) {
        updateWindow(currentTimeMs);
        return DutyCycleLimitMs > totalTxTimeMs_ ? (DutyCycleLimitMs - totalTxTimeMs_) : 0;
    }

private:
    uint32_t totalTxTimeMs_;
    uint32_t windowStartMs_;

    void updateWindow(uint32_t currentTimeMs) {
        if (currentTimeMs - windowStartMs_ >= WindowOneHourMs) {
            totalTxTimeMs_ = 0;
            windowStartMs_ = currentTimeMs;
        }
    }

    [[nodiscard]] int16_t readRssi() const {
        // Симуляція чистого ефіру (-92 дБм)
        return -92;
    }

    [[nodiscard]] bool isChannelClear() const {
        for (uint8_t i = 0; i < LbtSampleCount; ++i) {
            if (readRssi() > RssiThresholdDbm) {
                return false;
            }
        }
        return true;
    }
};
