#include <iostream>
#include <vector>
#include <array>
#include <cstring>
#include "cmsis_dap_handler.hpp"
#include "vfat_msd_emulator.hpp"

// Головний модуль тестування та демонстрування роботи CMSIS-DAP та MSD емуляції ST-Link V2.1
int main() {
    std::cout << "===========================================================\n";
    std::cout << " Архітектура прошивки ST-Link V2.1 (CMSIS-DAP & MSD Drag-n-Drop)\n";
    std::cout << "===========================================================\n\n";

    // 1. Створення об'єкта обробника протоколу CMSIS-DAP
    CmsisDapHandler dap_handler;

    // 2. Створення емулятора файлової системи FAT16 накопичувача USB MSD
    VfatMsdEmulator msd_emulator(dap_handler);

    // ---------------------------------------------------------------------
    // Сценарій А: Перевірка декодування та виконання команд CMSIS-DAP
    // ---------------------------------------------------------------------
    std::cout << "--- [1] Емуляція вхідного USB Bulk-пакета CMSIS-DAP ---\n";

    DapPacketBuffer rx_buf;
    DapPacketBuffer tx_buf;

    // Спроба підключення до SWD порту (Команда DAP_Connect)
    rx_buf.write_u8(static_cast<uint8_t>(DapCommand::Connect));
    rx_buf.write_u8(0x01); // Запит SWD порту

    if (dap_handler.process_packet(rx_buf, tx_buf)) {
        std::cout << "Відповідь CMSIS-DAP Connect: Status = 0x" 
                  << std::hex << static_cast<int>(tx_buf.read_u8(1)) << std::dec << "\n";
    }

    // Запит інформації про версію прошивки (DAP_Info)
    rx_buf.clear();
    rx_buf.write_u8(static_cast<uint8_t>(DapCommand::Info));
    rx_buf.write_u8(0x01); // ID версії

    if (dap_handler.process_packet(rx_buf, tx_buf)) {
        uint8_t len = tx_buf.read_u8(1);
        std::string version(reinterpret_cast<const char*>(&tx_buf.data[2]), len);
        std::cout << "Версія прошивки CMSIS-DAP: " << version << "\n\n";
    }

    // ---------------------------------------------------------------------
    // Сценарій Б: Обробка SCSI запиту INQUIRY від хоста USB MSD
    // ---------------------------------------------------------------------
    std::cout << "--- [2] Обробка SCSI Команд накопичувача USB MSD ---\n";

    // Формування структури SCSI CBW для запиту INQUIRY
    Cbw scsi_cbw{};
    scsi_cbw.signature = 0x43425355; // "USBC"
    scsi_cbw.tag = 0x01020304;
    scsi_cbw.data_transfer_length = 36;
    scsi_cbw.flags = 0x80; // In Data Transfer
    scsi_cbw.cb_length = 6;
    scsi_cbw.cb[0] = 0x12; // Opcode INQUIRY

    std::vector<uint8_t> cbw_bytes(sizeof(Cbw));
    std::memcpy(cbw_bytes.data(), &scsi_cbw, sizeof(Cbw));

    std::vector<uint8_t> scsi_response;
    Csw scsi_csw{};

    if (msd_emulator.process_scsi_cbw(cbw_bytes, scsi_response, scsi_csw)) {
        std::string vendor(reinterpret_cast<const char*>(&scsi_response[8]), 8);
        std::string product(reinterpret_cast<const char*>(&scsi_response[16]), 16);
        std::cout << "SCSI Device Vendor : " << vendor << "\n";
        std::cout << "SCSI Device Product: " << product << "\n";
        std::cout << "SCSI CSW Status    : " << static_cast<int>(scsi_csw.status) << " (Success)\n\n";
    }

    // ---------------------------------------------------------------------
    // Сценарій В: Емуляція Drag-and-Drop копіювання файлу FIRMWARE.BIN
    // ---------------------------------------------------------------------
    std::cout << "--- [3] Емуляція Drag-and-Drop прошивання мікроконтролера ---\n";

    // Емулюємо запис сектора Root Directory, де з'являється новий файл "FIRMWARE.BIN"
    std::array<uint8_t, FAT_SECTOR_SIZE> root_dir_sector{};
    auto* entry = reinterpret_cast<FatDirectoryEntry*>(root_dir_sector.data());
    std::memcpy(entry->filename, "FIRMWAREBIN", 11);
    entry->attributes = 0x20; // Archive
    entry->start_cluster = 3;
    entry->file_size = 2048;

    // Передаємо сектор каталогу в MSD емулятор
    msd_emulator.write_sector(130, root_dir_sector); // LBA кореневого каталогу

    // Послідовна передача 4 секторів бінарного прошивального образу (2048 байт)
    std::array<uint8_t, FAT_SECTOR_SIZE> dummy_firmware_data{};
    dummy_firmware_data.fill(0xAA); // Заповнюємо тестовим паттерном

    uint32_t data_lba_start = 162; // LBA першого кластера даних
    for (int i = 0; i < 4; ++i) {
        msd_emulator.write_sector(data_lba_start + i, dummy_firmware_data);
    }

    // Перевірка фінального стану прошивального автомата
    const auto& state = msd_emulator.get_flash_state();
    std::cout << "\nСтатус автомата прошивання : " 
              << (state.status == FlashStatus::Completed ? "Завершено успішно (Completed)" : "Помилка") << "\n";
    std::cout << "Всього байт прошито у Flash: " << state.total_bytes_received << " байт\n";
    std::cout << "Завершальна адреса Flash   : 0x" << std::hex 
              << (state.flash_base_address + state.current_offset) << std::dec << "\n\n";

    std::cout << "===========================================================\n";
    std::cout << " Програму завершено успішно.\n";
    std::cout << "===========================================================\n";

    return 0;
}
