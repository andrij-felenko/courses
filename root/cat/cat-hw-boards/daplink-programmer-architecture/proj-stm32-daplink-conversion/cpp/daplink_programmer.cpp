#include "daplink_programmer.hpp"
#include <iostream>
#include <iomanip>

namespace daplink {

DapLinkProgrammer::DapLinkProgrammer(SwdInterface& swd, PowerGuard& powerGuard)
    : m_swd(swd), m_powerGuard(powerGuard) {}

bool DapLinkProgrammer::initialize() {
    m_swd.initialize();
    m_targetInfo.reset();
    transitionTo(ProgrammerState::Disconnected);
    return true;
}

void DapLinkProgrammer::updatePowerState(float targetVoltage) {
    bool isPowered = m_powerGuard.updateTargetVoltage(targetVoltage);

    if (!isPowered) {
        if (m_state == ProgrammerState::Connected || m_state == ProgrammerState::Debugging) {
            std::cout << "[DapLinkProgrammer] Аварійне переривання сеансу через втрату V_TARGET!\n";
            transitionTo(ProgrammerState::Error);
        }
    }
}

bool DapLinkProgrammer::connectTarget() {
    std::cout << "[DapLinkProgrammer] Ініціалізація підключення до цільової плати...\n";

    if (!m_powerGuard.isTargetPowered()) {
        std::cout << "[DapLinkProgrammer] ПОМИЛКА: Цільова плата не знеживлена (V_TARGET < 1.8V).\n";
        transitionTo(ProgrammerState::Error);
        return false;
    }

    // Встановлюємо активний режим для тактування та даних
    m_swd.setSwclkMode(PinMode::OutputPushPull);
    m_swd.setSwdioMode(PinMode::OutputPushPull);

    // Виконуємо скидання SWD та процедуру переключення з JTAG на SWD
    if (!performSwdResetSequence()) {
        std::cout << "[DapLinkProgrammer] ПОМИЛКА: Спроба SWD Reset sequence зазнала невдачі.\n";
        m_swd.setHighZ();
        transitionTo(ProgrammerState::Error);
        return false;
    }

    // Зчитуємо регістр IDCODE
    if (!readTargetIdCode()) {
        std::cout << "[DapLinkProgrammer] ПОМИЛКА: Не вдалося зчитати IDCODE target MCU.\n";
        m_swd.setHighZ();
        transitionTo(ProgrammerState::Error);
        return false;
    }

    transitionTo(ProgrammerState::Connected);
    return true;
}

void DapLinkProgrammer::disconnectTarget() {
    std::cout << "[DapLinkProgrammer] Відключення від цільової плати...\n";
    m_swd.setHighZ();
    m_targetInfo.reset();
    transitionTo(ProgrammerState::Disconnected);
}

bool DapLinkProgrammer::startDebugSession() {
    if (m_state != ProgrammerState::Connected) {
        std::cout << "[DapLinkProgrammer] Запуск зневадження можливий лише у стані Connected!\n";
        return false;
    }

    if (!m_powerGuard.isTargetPowered()) {
        transitionTo(ProgrammerState::Error);
        return false;
    }

    std::cout << "[DapLinkProgrammer] Запуск сесії зневадження (Cortex-M Halt & Debug Mode)...\n";
    transitionTo(ProgrammerState::Debugging);
    return true;
}

void DapLinkProgrammer::stopDebugSession() {
    if (m_state == ProgrammerState::Debugging) {
        std::cout << "[DapLinkProgrammer] Зупинка сесії зневадження, повернення у режим Connected.\n";
        transitionTo(ProgrammerState::Connected);
    }
}

std::optional<uint32_t> DapLinkProgrammer::readRegister(uint32_t address) {
    if (m_state != ProgrammerState::Connected && m_state != ProgrammerState::Debugging) {
        std::cout << "[DapLinkProgrammer] Читання заблоковано: програматор не у режимі зневадження!\n";
        return std::nullopt;
    }

    if (!m_powerGuard.isTargetPowered()) {
        std::cout << "[DapLinkProgrammer] Втрата живлення під час читання!\n";
        transitionTo(ProgrammerState::Error);
        return std::nullopt;
    }

    std::cout << "  [SWD Read] Запит читання з адреси 0x" << std::hex << std::uppercase << address << std::dec << "\n";
    // Моделювання передачі SWD пакету читання
    m_swd.writeWord(address);
    uint32_t val = m_swd.readWord();
    // Повертаємо тестове значення для демонстрації
    if (address == 0xE000EDF0) { // DHCSR (Debug Halting Control and Status Register)
        val = 0x00030001; // C_DEBUGEN | C_HALT
    } else if (address == 0xE000EDFC) { // DEMCR
        val = 0x01000000; // TRCENA
    }
    return val;
}

bool DapLinkProgrammer::writeRegister(uint32_t address, uint32_t data) {
    if (m_state != ProgrammerState::Connected && m_state != ProgrammerState::Debugging) {
        std::cout << "[DapLinkProgrammer] Запис заблоковано: програматор не підключений!\n";
        return false;
    }

    if (!m_powerGuard.isTargetPowered()) {
        std::cout << "[DapLinkProgrammer] Втрата живлення під час запису!\n";
        transitionTo(ProgrammerState::Error);
        return false;
    }

    std::cout << "  [SWD Write] Запис 0x" << std::hex << std::uppercase << data 
              << " за адресою 0x" << address << std::dec << "\n";
    m_swd.writeWord(address);
    m_swd.writeWord(data);
    return true;
}

void DapLinkProgrammer::clearError() {
    if (m_state == ProgrammerState::Error) {
        std::cout << "[DapLinkProgrammer] Скидання стану помилки.\n";
        m_swd.setHighZ();
        transitionTo(ProgrammerState::Disconnected);
    }
}

bool DapLinkProgrammer::performSwdResetSequence() {
    std::cout << "  [SWD Sequence] Виконання SWD Line Reset (50+ CLK з SWDIO=1)...\n";
    // 50+ clock cycles with SWDIO high to reset target SWD state machine
    for (int i = 0; i < 56; ++i) {
        m_swd.writeSwclk(false);
        m_swd.writeSwdio(true);
        m_swd.writeSwclk(true);
    }

    // JTAG-to-SWD Switching Sequence: 0xE79E (16-bit)
    std::cout << "  [SWD Sequence] Передача JTAG-to-SWD switching sequence (0xE79E)...\n";
    constexpr uint16_t jtagToSwdSeq = 0xE79E;
    for (int i = 0; i < 16; ++i) {
        bool bit = (jtagToSwdSeq >> i) & 1U;
        m_swd.writeSwclk(false);
        m_swd.writeSwdio(bit);
        m_swd.writeSwclk(true);
    }

    // Another 56 clock cycles with SWDIO high
    for (int i = 0; i < 56; ++i) {
        m_swd.writeSwclk(false);
        m_swd.writeSwdio(true);
        m_swd.writeSwclk(true);
    }

    // 8 idle clock cycles with SWDIO low
    for (int i = 0; i < 8; ++i) {
        m_swd.writeSwclk(false);
        m_swd.writeSwdio(false);
        m_swd.writeSwclk(true);
    }
    m_swd.writeSwclk(false);
    return true;
}

bool DapLinkProgrammer::readTargetIdCode() {
    std::cout << "  [SWD Sequence] Читання DP IDCODE (Debug Port ID Register)...\n";
    // Типовий IDCODE ARM Cortex-M4 (STM32F4/NXP LPC/Nordic nRF52) = 0x2BA01477
    constexpr uint32_t mockIdCode = 0x2BA01477;
    
    TargetInfo info;
    info.idcode = mockIdCode;
    info.designerID = (mockIdCode >> 1) & 0x7FF;   // Bits [11:1] -> ARM (0x477)
    info.partNumber = (mockIdCode >> 12) & 0xFFFF;  // Bits [27:12] -> Cortex-M4 (0xBA01)
    info.revision = (mockIdCode >> 28) & 0xF;       // Bits [31:28] -> Rev 2

    m_targetInfo = info;
    return true;
}

void DapLinkProgrammer::transitionTo(ProgrammerState newState) {
    std::cout << "[DapLinkProgrammer] Зміна стану: "
              << programmerStateToString(m_state) << " -> "
              << programmerStateToString(newState) << "\n";
    m_state = newState;
}

} // namespace daplink
