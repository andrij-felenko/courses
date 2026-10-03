#include "cmsis_dap_handler.hpp"
#include <iostream>
#include <cstring>
#include <algorithm>

// Адреси регістрів Core Debug та Flash контролера цільового STM32
constexpr uint32_t DHCSR_REG = 0xE000EDF0; // Core Debug Halting Control/Status
constexpr uint32_t AIRCR_REG = 0xE000ED0C; // Application Interrupt/Reset Control
constexpr uint32_t DHCSR_KEY = 0xA05F0000;

constexpr uint32_t STM32_FLASH_BASE = 0x40022000;
constexpr uint32_t FLASH_KEYR     = STM32_FLASH_BASE + 0x04;
constexpr uint32_t FLASH_SR       = STM32_FLASH_BASE + 0x0C;
constexpr uint32_t FLASH_CR       = STM32_FLASH_BASE + 0x10;
constexpr uint32_t FLASH_AR       = STM32_FLASH_BASE + 0x14;

constexpr uint32_t FLASH_KEY1 = 0x45670123;
constexpr uint32_t FLASH_KEY2 = 0xCDEF89AB;

constexpr uint32_t FLASH_CR_PG   = (1U << 0);
constexpr uint32_t FLASH_CR_PER  = (1U << 1);
constexpr uint32_t FLASH_CR_STRT = (1U << 6);
constexpr uint32_t FLASH_CR_LOCK = (1U << 7);
constexpr uint32_t FLASH_SR_BSY  = (1U << 0);

CmsisDapHandler::CmsisDapHandler() = default;

bool CmsisDapHandler::connect_swd() {
    port_mode_ = SwdPortMode::SWD;
    swclk_pin_ = true;
    swdio_pin_ = true;
    status_led_ = true;
    cached_select_reg_ = 0xFFFFFFFF;
    
    // Ініціалізація SWD послідовності скидання (50+ тактів SWCLK при High SWDIO)
    uint32_t idcode = 0;
    if (swd_read_dp(0x00, idcode)) {
        std::cout << "[CMSIS-DAP] З'єднання SWD встановлено. Target IDCODE: 0x"
                  << std::hex << idcode << std::dec << "\n";
        return true;
    }
    return false;
}

void CmsisDapHandler::disconnect() {
    port_mode_ = SwdPortMode::Disabled;
    status_led_ = false;
    std::cout << "[CMSIS-DAP] SWD-сесію завершено.\n";
}

bool CmsisDapHandler::set_clock(uint32_t clock_hz) {
    if (clock_hz == 0) return false;
    clock_hz_ = clock_hz;
    return true;
}

bool CmsisDapHandler::swd_write_dp(uint8_t reg_addr, uint32_t data) {
    if (port_mode_ == SwdPortMode::Disabled) return false;
    // Симуляція запису в регістр Debug Port (DP) по лінії SWD
    (void)reg_addr;
    (void)data;
    return true;
}

bool CmsisDapHandler::swd_read_dp(uint8_t reg_addr, uint32_t& data) {
    if (port_mode_ == SwdPortMode::Disabled) return false;
    if (reg_addr == 0x00) {
        data = 0x2BA01477; // Стандартний IDCODE ARM Cortex-M4 (STM32F4)
    } else {
        data = 0x00000000;
    }
    return true;
}

bool CmsisDapHandler::swd_write_ap(uint8_t reg_addr, uint32_t data) {
    if (port_mode_ == SwdPortMode::Disabled) return false;
    (void)reg_addr;
    (void)data;
    return true;
}

bool CmsisDapHandler::swd_read_ap(uint8_t reg_addr, uint32_t& data) {
    if (port_mode_ == SwdPortMode::Disabled) return false;
    (void)reg_addr;
    data = 0x00000000;
    return true;
}

bool CmsisDapHandler::swd_read_mem32(uint32_t address, uint32_t& data) {
    // Встановлення адреси в TAR (Transfer Address Register) MEM-AP та зчитування DRW
    if (!swd_write_ap(0x04, address)) return false;
    return swd_read_ap(0x0C, data);
}

bool CmsisDapHandler::swd_write_mem32(uint32_t address, uint32_t data) {
    if (!swd_write_ap(0x04, address)) return false;
    return swd_write_ap(0x0C, data);
}

bool CmsisDapHandler::target_halt() {
    std::cout << "[CMSIS-DAP] Зупинка ядра цільового МК (Halt)...\n";
    // Запис у DHCSR: C_HALT | C_DEBUGEN
    return swd_write_mem32(DHCSR_REG, DHCSR_KEY | 0x03);
}

bool CmsisDapHandler::target_resume() {
    std::cout << "[CMSIS-DAP] Відновлення виконання цільового МК (Resume)...\n";
    return swd_write_mem32(DHCSR_REG, DHCSR_KEY | 0x00);
}

bool CmsisDapHandler::target_flash_unlock() {
    std::cout << "[CMSIS-DAP] Розблокування контролера Flash пам'яті...\n";
    if (!swd_write_mem32(FLASH_KEYR, FLASH_KEY1)) return false;
    return swd_write_mem32(FLASH_KEYR, FLASH_KEY2);
}

bool CmsisDapHandler::target_flash_erase_sector(uint32_t sector_address) {
    std::cout << "[CMSIS-DAP] Стирання сектора Flash за адресою: 0x" 
              << std::hex << sector_address << std::dec << "...\n";
    // Встановлення біта PER (Page/Sector Erase) та адреси
    if (!swd_write_mem32(FLASH_CR, FLASH_CR_PER)) return false;
    if (!swd_write_mem32(FLASH_AR, sector_address)) return false;
    if (!swd_write_mem32(FLASH_CR, FLASH_CR_PER | FLASH_CR_STRT)) return false;
    
    // Очікування завершення операції (BSY == 0)
    uint32_t sr = 0;
    for (int i = 0; i < 100; ++i) {
        swd_read_mem32(FLASH_SR, sr);
        if ((sr & FLASH_SR_BSY) == 0) break;
    }
    swd_write_mem32(FLASH_CR, 0); // Очищення бітів керування
    return true;
}

bool CmsisDapHandler::target_flash_program_page(uint32_t address, std::span<const uint8_t> data) {
    if (data.empty()) return true;
    
    // Вмикаємо режим програмування Flash (PG)
    swd_write_mem32(FLASH_CR, FLASH_CR_PG);

    // Запис даних словами по 32 біти / півсловами по 16 біт
    for (size_t offset = 0; offset < data.size(); offset += 4) {
        uint32_t word = 0xFFFFFFFF;
        size_t chunk = std::min<size_t>(4, data.size() - offset);
        std::memcpy(&word, data.data() + offset, chunk);

        if (!swd_write_mem32(address + static_cast<uint32_t>(offset), word)) {
            swd_write_mem32(FLASH_CR, 0);
            return false;
        }
    }

    swd_write_mem32(FLASH_CR, 0);
    return true;
}

bool CmsisDapHandler::target_reset_and_run() {
    std::cout << "[CMSIS-DAP] Перезавантаження та запуск цільового пристрою...\n";
    // Запис біта SYSRESETREQ у регістр AIRCR
    swd_write_mem32(AIRCR_REG, 0x05FA0004);
    return target_resume();
}

bool CmsisDapHandler::process_packet(const DapPacketBuffer& rx_buf, DapPacketBuffer& tx_buf) {
    tx_buf.clear();
    if (rx_buf.length == 0) return false;

    auto cmd = static_cast<DapCommand>(rx_buf.read_u8(0));

    switch (cmd) {
        case DapCommand::Info:
            handle_cmd_info(rx_buf, tx_buf);
            break;
        case DapCommand::Connect:
            handle_cmd_connect(rx_buf, tx_buf);
            break;
        case DapCommand::Disconnect:
            handle_cmd_disconnect(rx_buf, tx_buf);
            break;
        case DapCommand::Transfer:
            handle_cmd_transfer(rx_buf, tx_buf);
            break;
        case DapCommand::SwjClock:
            handle_cmd_swj_clock(rx_buf, tx_buf);
            break;
        case DapCommand::SwjPins:
            handle_cmd_swj_pins(rx_buf, tx_buf);
            break;
        default:
            tx_buf.write_u8(static_cast<uint8_t>(cmd));
            tx_buf.write_u8(static_cast<uint8_t>(DapResponseStatus::Error));
            break;
    }
    return true;
}

void CmsisDapHandler::handle_cmd_info(const DapPacketBuffer& rx, DapPacketBuffer& tx) {
    uint8_t info_id = rx.read_u8(1);
    tx.write_u8(static_cast<uint8_t>(DapCommand::Info));

    if (info_id == 0x01) { // FW Version
        std::string_view version = "2.1.0";
        tx.write_u8(static_cast<uint8_t>(version.length()));
        for (char c : version) tx.write_u8(static_cast<uint8_t>(c));
    } else if (info_id == 0x02) { // Target Device Name
        std::string_view name = "STM32F4xx CMSIS-DAP";
        tx.write_u8(static_cast<uint8_t>(name.length()));
        for (char c : name) tx.write_u8(static_cast<uint8_t>(c));
    } else {
        tx.write_u8(0);
    }
}

void CmsisDapHandler::handle_cmd_connect(const DapPacketBuffer& rx, DapPacketBuffer& tx) {
    uint8_t req_port = rx.read_u8(1);
    tx.write_u8(static_cast<uint8_t>(DapCommand::Connect));

    if (req_port == 1 || req_port == 0) { // SWD / Default
        connect_swd();
        tx.write_u8(static_cast<uint8_t>(SwdPortMode::SWD));
    } else {
        tx.write_u8(static_cast<uint8_t>(SwdPortMode::Disabled));
    }
}

void CmsisDapHandler::handle_cmd_disconnect(const DapPacketBuffer& rx, DapPacketBuffer& tx) {
    (void)rx;
    disconnect();
    tx.write_u8(static_cast<uint8_t>(DapCommand::Disconnect));
    tx.write_u8(static_cast<uint8_t>(DapResponseStatus::Ok));
}

void CmsisDapHandler::handle_cmd_swj_clock(const DapPacketBuffer& rx, DapPacketBuffer& tx) {
    uint32_t clock_speed = rx.read_u32(1);
    set_clock(clock_speed);
    tx.write_u8(static_cast<uint8_t>(DapCommand::SwjClock));
    tx.write_u8(static_cast<uint8_t>(DapResponseStatus::Ok));
}

void CmsisDapHandler::handle_cmd_swj_pins(const DapPacketBuffer& rx, DapPacketBuffer& tx) {
    uint8_t pin_output = rx.read_u8(1);
    uint8_t pin_select = rx.read_u8(2);

    if (pin_select & 0x01) swclk_pin_ = (pin_output & 0x01) != 0;
    if (pin_select & 0x02) swdio_pin_ = (pin_output & 0x02) != 0;
    if (pin_select & 0x80) nrst_pin_  = (pin_output & 0x80) != 0;

    tx.write_u8(static_cast<uint8_t>(DapCommand::SwjPins));
    uint8_t in_val = (swclk_pin_ ? 0x01 : 0) | (swdio_pin_ ? 0x02 : 0) | (nrst_pin_ ? 0x80 : 0);
    tx.write_u8(in_val);
}

void CmsisDapHandler::handle_cmd_transfer(const DapPacketBuffer& rx, DapPacketBuffer& tx) {
    uint8_t transfer_count = rx.read_u8(2);
    tx.write_u8(static_cast<uint8_t>(DapCommand::Transfer));
    tx.write_u8(transfer_count); // Успішно виконано транзакцій
    tx.write_u8(0x01);           // OK (ACK = 1)

    size_t rx_idx = 3;
    for (uint8_t i = 0; i < transfer_count; ++i) {
        uint8_t req = rx.read_u8(rx_idx++);
        bool is_write = (req & 0x02) == 0;
        bool is_ap    = (req & 0x01) != 0;
        uint8_t reg   = (req & 0x0C);

        if (is_write) {
            uint32_t data = rx.read_u32(rx_idx);
            rx_idx += 4;
            if (is_ap) swd_write_ap(reg, data);
            else swd_write_dp(reg, data);
        } else {
            uint32_t val = 0;
            if (is_ap) swd_read_ap(reg, val);
            else swd_read_dp(reg, val);
            tx.write_u32(val);
        }
    }
}
