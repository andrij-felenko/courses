#include "daplink_controller.hpp"
#include <iostream>
#include <iomanip>

/**
 * @brief Встановлення з'єднання з цільовим мікроконтролером через режим SWD
 */
bool DAPLinkController::connect(DAPPort port) {
    DAPPacket req;
    req.append_byte(static_cast<std::uint8_t>(DAPCommand::DAP_CONNECT));
    req.append_byte(static_cast<std::uint8_t>(port));

    std::cout << "[DAPLink] Надсилання команди DAP_CONNECT (Port: SWD)..." << std::endl;
    DAPPacket resp = send_packet(req);

    if (resp.buffer.size() >= 2 && resp.buffer[0] == static_cast<std::uint8_t>(DAPCommand::DAP_CONNECT)) {
        if (resp.buffer[1] == static_cast<std::uint8_t>(DAPPort::SWD)) {
            is_connected_ = true;
            std::cout << "[DAPLink] Успішно підключено до шини SWD." << std::endl;
            return true;
        }
    }
    std::cerr << "[DAPLink] Помилка підключення до шини SWD." << std::endl;
    return false;
}

/**
 * @brief Закриття сесії зневадження
 */
bool DAPLinkController::disconnect() {
    DAPPacket req;
    req.append_byte(static_cast<std::uint8_t>(DAPCommand::DAP_DISCONNECT));

    std::cout << "[DAPLink] Відключення сесії зневадження..." << std::endl;
    DAPPacket resp = send_packet(req);

    is_connected_ = false;
    return (resp.buffer.size() >= 2 && resp.buffer[1] == static_cast<std::uint8_t>(DAPStatus::DAP_OK));
}

/**
 * @brief Налаштування тактової частоти шини SWD
 */
bool DAPLinkController::set_clock(std::uint32_t clock_hz) {
    DAPPacket req;
    req.append_byte(static_cast<std::uint8_t>(DAPCommand::DAP_SWJ_CLOCK));
    req.append_u32(clock_hz);

    std::cout << "[DAPLink] Налаштування тактової частоти SWJ Clock: " << clock_hz << " Гц..." << std::endl;
    DAPPacket resp = send_packet(req);

    if (resp.buffer.size() >= 2 && resp.buffer[1] == static_cast<std::uint8_t>(DAPStatus::DAP_OK)) {
        current_clock_ = clock_hz;
        return true;
    }
    return false;
}

/**
 * @brief Зчитування ідентифікаційного коду ядра CoreSight IDCODE через транзакцію SWD
 */
std::optional<std::uint32_t> DAPLinkController::read_idcode() {
    if (!is_connected_) {
        std::cerr << "[DAPLink] Помилка: сесію не ініціалізовано." << std::endl;
        return std::nullopt;
    }

    DAPPacket req;
    req.append_byte(static_cast<std::uint8_t>(DAPCommand::DAP_TRANSFER));
    req.append_byte(0x00); /* Індекс пристрою DAP Index = 0 */
    req.append_byte(0x01); /* Кількість транзакцій = 1 */
    req.append_byte(0x02); /* Transfer Request: Read DP Register 0x00 (IDCODE) */

    std::cout << "[DAPLink] Читання регістру IDCODE (DP Reg 0x00)..." << std::endl;
    DAPPacket resp = send_packet(req);

    /* Формат відповіді: [0] Command ID, [1] Count, [2] Response Status (ACK), [3..6] Data */
    if (resp.buffer.size() >= 7 && resp.buffer[2] == 0x01) { /* ACK == OK (0x01) */
        std::uint32_t idcode = static_cast<std::uint32_t>(resp.buffer[3]) |
                              (static_cast<std::uint32_t>(resp.buffer[4]) << 8) |
                              (static_cast<std::uint32_t>(resp.buffer[5]) << 16) |
                              (static_cast<std::uint32_t>(resp.buffer[6]) << 24);
        return idcode;
    }

    std::cerr << "[DAPLink] Збій читання IDCODE (Немає відповіді ACK)." << std::endl;
    return std::nullopt;
}

/**
 * @brief Формування імпульсу скидання цільового мікроконтролера
 */
bool DAPLinkController::reset_target() {
    std::cout << "[DAPLink] Апаратне скидання цілі: утримання nRESET = LOW..." << std::endl;
    set_nreset(false); /* Притягування ліній nRESET до GND */
    
    DAPPacket req;
    req.append_byte(static_cast<std::uint8_t>(DAPCommand::DAP_RESET_TARGET));
    DAPPacket resp = send_packet(req);

    set_nreset(true);  /* Відпускання лінії nRESET у HIGH */
    std::cout << "[DAPLink] Зняття сигналу скидання nRESET = HIGH." << std::endl;

    return (resp.buffer.size() >= 2 && resp.buffer[1] == static_cast<std::uint8_t>(DAPStatus::DAP_OK));
}

void DAPLinkController::set_swclk(bool level) {
    std::cout << "[HAL GPIO] SWCLK -> " << (level ? "HIGH" : "LOW") << std::endl;
}

void DAPLinkController::set_swdio(bool level) {
    std::cout << "[HAL GPIO] SWDIO -> " << (level ? "HIGH" : "LOW") << std::endl;
}

void DAPLinkController::set_nreset(bool level) {
    std::cout << "[HAL GPIO] nRESET -> " << (level ? "HIGH (High-Z)" : "LOW (GND)") << std::endl;
}

/**
 * @brief Симуляція передачі USB-пакета через Bulk-ендпоінт пристрою
 */
DAPPacket DAPLinkController::send_packet(const DAPPacket& request) {
    DAPPacket response;
    if (request.buffer.empty()) return response;

    auto cmd = static_cast<DAPCommand>(request.buffer[0]);
    response.append_byte(request.buffer[0]);

    switch (cmd) {
        case DAPCommand::DAP_CONNECT:
            response.append_byte(static_cast<std::uint8_t>(DAPPort::SWD));
            break;
        case DAPCommand::DAP_SWJ_CLOCK:
        case DAPCommand::DAP_DISCONNECT:
        case DAPCommand::DAP_RESET_TARGET:
            response.append_byte(static_cast<std::uint8_t>(DAPStatus::DAP_OK));
            break;
        case DAPCommand::DAP_TRANSFER:
            response.append_byte(0x01); /* Count = 1 */
            response.append_byte(0x01); /* ACK = OK (0x01) */
            /* Симуляція IDCODE для ARM Cortex-M4 (STM32F4 / Cortex-M): 0x2BA01477 */
            response.append_u32(0x2BA01477);
            break;
        default:
            response.append_byte(static_cast<std::uint8_t>(DAPStatus::DAP_ERROR));
            break;
    }
    return response;
}
