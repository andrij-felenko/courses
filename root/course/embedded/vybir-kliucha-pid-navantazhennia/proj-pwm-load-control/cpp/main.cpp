#include <cstdint>
#include <algorithm>
#include <chrono>

/**
 * @brief Безпечний RAII-драйвер силового перемикача з плавним пуском
 */
class PwmPowerDriver {
public:
    explicit constexpr PwmPowerDriver(uint8_t gpioPin, uint16_t rampStep = 20) noexcept
        : m_gpioPin(gpioPin),
          m_rampStep(rampStep),
          m_currentDuty(0),
          m_targetDuty(0),
          m_enabled(false) {}

    ~PwmPowerDriver() noexcept {
        emergencyStop();
    }

    PwmPowerDriver(const PwmPowerDriver&) = delete;
    PwmPowerDriver& operator=(const PwmPowerDriver&) = delete;
    PwmPowerDriver(PwmPowerDriver&&) noexcept = default;
    PwmPowerDriver& operator=(PwmPowerDriver&&) noexcept = default;

    void setTargetDuty(uint16_t targetPerMille) noexcept {
        m_targetDuty = std::min<uint16_t>(targetPerMille, 1000);
        m_enabled = (m_targetDuty > 0);
    }

    void emergencyStop() noexcept {
        m_targetDuty = 0;
        m_currentDuty = 0;
        m_enabled = false;
        writeHardwarePwm(0);
    }

    void updateTick() noexcept {
        if (m_currentDuty < m_targetDuty) {
            m_currentDuty = std::min<uint16_t>(m_targetDuty, m_currentDuty + m_rampStep);
            writeHardwarePwm(m_currentDuty);
        } else if (m_currentDuty > m_targetDuty) {
            const uint16_t step = std::min(m_rampStep, m_currentDuty);
            m_currentDuty = (m_currentDuty - step < m_targetDuty) ? m_targetDuty : (m_currentDuty - step);
            writeHardwarePwm(m_currentDuty);
        }
    }

    [[nodiscard]] uint16_t getCurrentDuty() const noexcept { return m_currentDuty; }
    [[nodiscard]] bool isRunning() const noexcept { return m_enabled; }

private:
    void writeHardwarePwm(uint16_t dutyPerMille) noexcept {
        // Платформовий запис значення шпаруватості в апаратний регістр CCR таймера
        (void)dutyPerMille;
        (void)m_gpioPin;
    }

    uint8_t  m_gpioPin;
    uint16_t m_rampStep;
    uint16_t m_currentDuty;
    uint16_t m_targetDuty;
    bool     m_enabled;
};
