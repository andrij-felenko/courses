#include <cstdint>
#include <concepts>
#include <span>
#include <atomic>

namespace PowerCut {

/* Клас апаратного драйвера комутації живлення з RAII-гарантією dead-time */
class PowerSwitchController {
public:
    static constexpr std::uint32_t PinHighSide = (1U << 4);
    static constexpr std::uint32_t PinCrowbar  = (1U << 5);
    static constexpr std::uint32_t PinTrigger  = (1U << 0);

    PowerSwitchController() noexcept {
        initHardware();
        enablePower();
    }

    ~PowerSwitchController() noexcept {
        disablePowerSafe();
    }

    void enablePower() noexcept {
        // Закриваємо розрядний N-MOSFET
        setPinState(PinCrowbar, false);
        insertDeadTime();
        // Відкриваємо P-MOSFET верхнього плеча (Active LOW)
        setPinState(PinHighSide, false);
        isPowered_.store(true, std::memory_order_release);
    }

    void emergencyCut() noexcept {
        // Миттєво розмикаємо верхнє плече
        setPinState(PinHighSide, true);
        insertDeadTime();
        // Вмикаємо активний розряд шини на землю
        setPinState(PinCrowbar, true);
        isPowered_.store(false, std::memory_order_release);
    }

    void armTrigger(std::uint32_t delayMicroseconds, std::uint32_t cutDurationMs) noexcept {
        targetDelayUs_.store(delayMicroseconds, std::memory_order_relaxed);
        cutDurationMs_.store(cutDurationMs, std::memory_order_relaxed);
        cycleComplete_.store(false, std::memory_order_release);
        
        enablePower();
        isArmed_.store(true, std::memory_order_release);
    }

    void onTriggerReceived() noexcept {
        if (!isArmed_.load(std::memory_order_acquire)) {
            return;
        }

        const auto delay = targetDelayUs_.load(std::memory_order_relaxed);
        if (delay == 0) {
            emergencyCut();
            finalizeCycle();
        } else {
            startHardwareTimer(delay);
        }
    }

    void onTimerExpired() noexcept {
        if (isArmed_.load(std::memory_order_acquire)) {
            emergencyCut();
            finalizeCycle();
        }
    }

    [[nodiscard]] bool isCycleComplete() const noexcept {
        return cycleComplete_.load(std::memory_order_acquire);
    }

    [[nodiscard]] std::uint64_t getTotalCycles() const noexcept {
        return totalCycles_.load(std::memory_order_relaxed);
    }

private:
    std::atomic<bool>          isArmed_{false};
    std::atomic<bool>          isPowered_{false};
    std::atomic<bool>          cycleComplete_{false};
    std::atomic<std::uint32_t> targetDelayUs_{0};
    std::atomic<std::uint32_t> cutDurationMs_{50};
    std::atomic<std::uint64_t> totalCycles_{0};

    static void insertDeadTime() noexcept {
        #if defined(__ARM_ARCH)
        asm volatile("nop; nop; nop; nop;");
        #endif
    }

    void initHardware() noexcept {
        // Налаштування GPIO регістрів та таймерів мікроконтролера
    }

    void setPinState([[maybe_unused]] std::uint32_t pin, [[maybe_unused]] bool state) noexcept {
        // Прямий бітовий запис у BSRR регістр порту
    }

    void startHardwareTimer([[maybe_unused]] std::uint32_t us) noexcept {
        // Запуск 32-бітного апаратного таймера TIM2
    }

    void finalizeCycle() noexcept {
        isArmed_.store(false, std::memory_order_release);
        cycleComplete_.store(true, std::memory_order_release);
        totalCycles_.fetch_add(1, std::memory_order_relaxed);
    }

    void disablePowerSafe() noexcept {
        setPinState(PinHighSide, true);
        setPinState(PinCrowbar, false);
        isPowered_.store(false, std::memory_order_release);
    }
};

} // namespace PowerCut
