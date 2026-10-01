#ifndef DAPLINK_PROGRAMMER_HPP
#define DAPLINK_PROGRAMMER_HPP

#include "swd_interface.hpp"
#include <cstdint>
#include <string_view>
#include <optional>

namespace daplink {

/**
 * @brief Стани кінцевого автомата програматора DAPLink
 */
enum class ProgrammerState : uint8_t {
    Disconnected, ///< Робочі лінії у стан High-Z, цільова плата не підключена
    Connected,    ///< Виконано фізичне та логічне підключення SWD, зчитано IDCODE
    Debugging,    ///< Активна сесія зневадження (зупинка ядра, читання/запис регістрів)
    Error         ///< Аварійний стан (втрата живлення цільової плати, збій SWD)
};

/**
 * @brief Перетворення стану програматора у текстовий опис українською мовою
 */
constexpr std::string_view programmerStateToString(ProgrammerState state) noexcept {
    switch (state) {
        case ProgrammerState::Disconnected: return "Відключений (High-Z)";
        case ProgrammerState::Connected:    return "Підключений (SWD активний)";
        case ProgrammerState::Debugging:    return "Зневадження (Debug Active)";
        case ProgrammerState::Error:        return "Помилка (Fault/Power Failure)";
    }
    return "Невідомий стан";
}

/**
 * @brief Структура інформації про ідентифікатор цільового мікроконтролера (IDCODE)
 */
struct TargetInfo {
    uint32_t idcode{0};
    uint16_t designerID{0};
    uint16_t partNumber{0};
    uint8_t revision{0};
};

/**
 * @brief Головний клас керування програматором DAPLink та кінцевим автоматом
 */
class DapLinkProgrammer {
public:
    DapLinkProgrammer(SwdInterface& swd, PowerGuard& powerGuard);

    /**
     * @brief Ініціалізація підсистеми програматора
     */
    bool initialize();

    /**
     * @brief Перевірка та оновлення стану живлення цільової плати
     * @param targetVoltage Виміряна напруга V_TARGET у вольтах
     */
    void updatePowerState(float targetVoltage);

    /**
     * @brief Виконання процедури підключення до цільового MCU через SWD
     * @return true у разі успішного зчитування IDCODE та встановлення зв'язку
     */
    bool connectTarget();

    /**
     * @brief Безпечне відключення від цільової плати та переведення ліній у High-Z
     */
    void disconnectTarget();

    /**
     * @brief Запуск сесії зневадження (перехід у стан Debugging)
     */
    bool startDebugSession();

    /**
     * @brief Зупинка сесії зневадження та повернення у стан Connected
     */
    void stopDebugSession();

    /**
     * @brief Читання значення з регістра target MCU через SWD
     * @param address Адреса регістра/пам'яті
     * @return Зчитане значення або std::nullopt у разі помилки
     */
    std::optional<uint32_t> readRegister(uint32_t address);

    /**
     * @brief Запис значення у регістр target MCU через SWD
     * @param address Адреса регістра/пам'яті
     * @param data Значення для запису
     * @return true у разі успішного запису
     */
    bool writeRegister(uint32_t address, uint32_t data);

    /**
     * @brief Отримання поточного стану кінцевого автомата
     */
    [[nodiscard]] ProgrammerState getState() const noexcept { return m_state; }

    /**
     * @brief Отримання інформації про підключений мікроконтролер
     */
    [[nodiscard]] std::optional<TargetInfo> getTargetInfo() const noexcept { return m_targetInfo; }

    /**
     * @brief Скидання аварійного стану після усунення причини несправності
     */
    void clearError();

private:
    bool performSwdResetSequence();
    bool readTargetIdCode();
    void transitionTo(ProgrammerState newState);

    SwdInterface& m_swd;
    PowerGuard& m_powerGuard;
    ProgrammerState m_state{ProgrammerState::Disconnected};
    std::optional<TargetInfo> m_targetInfo{};
};

} // namespace daplink

#endif // DAPLINK_PROGRAMMER_HPP
