/* ============================================================================
 * SpiFlashDriver.hpp — Драйвер Flash з використанням RAII ScopedPowerLock (C++)
 * ============================================================================ */
#pragma once

#include "PowerManager.hpp"
#include <span>

namespace emb::drivers {

class SpiFlashDriver final : public pm::IPowerClient {
public:
    SpiFlashDriver() noexcept {
        pm::PowerManager::instance().registerClient(this);
    }

    [[nodiscard]] std::string_view name() const noexcept override {
        return "SpiFlash";
    }

    [[nodiscard]] bool preSleep(pm::Mode targetMode) noexcept override {
        if (m_busy.load(std::memory_order_acquire)) {
            return false;
        }

        if (targetMode == pm::Mode::Stop || targetMode == pm::Mode::Standby) {
            // Переведення зовнішньої Flash у Deep Power Down (0xB9)
            // Ізоляція виводів SPI в стан Analog High-Z
        }
        return true;
    }

    void postWakeup(pm::Mode fromMode) noexcept override {
        if (fromMode == pm::Mode::Stop || fromMode == pm::Mode::Standby) {
            // Відновлення пінів SPI та пробудження Flash (0xAB)
        }
    }

    // Синхронний запис із гарантією збереження живлення через RAII блокування
    bool writeBuffer(uint32_t address, std::span<const uint8_t> data) noexcept {
        (void)address; (void)data;

        // Автоматично захоплює блокування NoStop при вході в область видимості
        // та звільняє його при будь-якому виході (навіть при помилці)
        pm::ScopedPowerLock lockGuard(pm::Lock::NoStop);

        m_busy.store(true, std::memory_order_release);

        // Виконання передачі по шині SPI...

        m_busy.store(false, std::memory_order_release);
        return true;
    }

private:
    std::atomic<bool> m_busy{false};
};

} // namespace emb::drivers
