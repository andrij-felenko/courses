#include "vfat_msd_emulator.hpp"
#include <cstring>
#include <algorithm>
#include <iostream>

VfatMsdEmulator::VfatMsdEmulator(CmsisDapHandler& dap_handler)
    : dap_handler_(dap_handler) {}

void VfatMsdEmulator::generate_boot_sector(std::span<uint8_t, FAT_SECTOR_SIZE> sector) {
    sector.fill(0);

    // JMP instruction
    sector[0] = 0xEB; sector[1] = 0x3C; sector[2] = 0x90;
    std::memcpy(&sector[3], "STLINK  ", 8); // OEM Name

    // BPB (BIOS Parameter Block)
    uint16_t bytes_per_sector = FAT_SECTOR_SIZE;
    uint16_t reserved_sectors = RESERVED_SECTORS;
    uint8_t  fats = NUMBER_OF_FATS;
    uint16_t root_entries = ROOT_DIR_ENTRIES;
    uint32_t total_sectors = TOTAL_SECTORS;
    uint16_t sectors_per_fat = SECTORS_PER_FAT;

    std::memcpy(&sector[11], &bytes_per_sector, 2);
    sector[13] = SECTORS_PER_CLUSTER;
    std::memcpy(&sector[14], &reserved_sectors, 2);
    sector[16] = fats;
    std::memcpy(&sector[17], &root_entries, 2);
    sector[21] = 0xF8; // Media descriptor (Hard Disk / Removable)
    std::memcpy(&sector[22], &sectors_per_fat, 2);
    std::memcpy(&sector[32], &total_sectors, 4);

    // Extended BPB (FAT16)
    sector[36] = 0x80; // Drive number
    sector[38] = 0x29; // Boot signature
    uint32_t volume_id = 0x12345678;
    std::memcpy(&sector[39], &volume_id, 4);
    std::memcpy(&sector[43], "STLINK_V2_1", 11);
    std::memcpy(&sector[54], "FAT16   ", 8);

    // Boot code signature
    sector[510] = 0x55;
    sector[511] = 0xAA;
}

void VfatMsdEmulator::generate_fat_sector(uint32_t lba, std::span<uint8_t, FAT_SECTOR_SIZE> sector) {
    sector.fill(0);
    uint32_t fat_offset_lba = (lba >= FAT2_LBA) ? (lba - FAT2_LBA) : (lba - FAT1_LBA);

    if (fat_offset_lba == 0) {
        // Перші два записи FAT16 спеціальні: Media Descriptor + EOF
        uint16_t entry0 = 0xFFF8;
        uint16_t entry1 = 0xFFFF;
        std::memcpy(&sector[0], &entry0, 2);
        std::memcpy(&sector[2], &entry1, 2);

        // Кластер 2 належить файлу INFO_DAP.TXT (End of Cluster chain)
        uint16_t entry2 = 0xFFFF;
        std::memcpy(&sector[4], &entry2, 2);
    }
}

void VfatMsdEmulator::generate_root_dir_sector(uint32_t lba, std::span<uint8_t, FAT_SECTOR_SIZE> sector) {
    sector.fill(0);
    uint32_t offset_idx = lba - ROOT_DIR_LBA;

    if (offset_idx == 0) {
        auto* entries = reinterpret_cast<FatDirectoryEntry*>(sector.data());

        // Запис 1: Том (Volume Label)
        std::memcpy(entries[0].filename, "STLINK_V2_1", 11);
        entries[0].attributes = 0x08; // Volume ID

        // Запис 2: Файл статусу INFO_DAP.TXT
        std::memcpy(entries[1].filename, "INFO_DAPTXT", 11);
        entries[1].attributes = 0x20; // Archive
        entries[1].start_cluster = 2;
        entries[1].file_size = 64; // Фіксований розмір інформаційного тексту
    }
}

void VfatMsdEmulator::read_sector(uint32_t lba, std::span<uint8_t, FAT_SECTOR_SIZE> sector_out) {
    if (lba == 0) {
        generate_boot_sector(sector_out);
    } else if ((lba >= FAT1_LBA && lba < FAT2_LBA) || (lba >= FAT2_LBA && lba < ROOT_DIR_LBA)) {
        generate_fat_sector(lba, sector_out);
    } else if (lba >= ROOT_DIR_LBA && lba < DATA_START_LBA) {
        generate_root_dir_sector(lba, sector_out);
    } else if (lba == DATA_START_LBA) {
        // Зчитування вмісту файлу INFO_DAP.TXT (Кластер 2)
        sector_out.fill(0);
        std::string_view info = "ST-Link V2.1 Firmware Architecture\nCMSIS-DAP Drag-and-Drop Active\n";
        std::memcpy(sector_out.data(), info.data(), info.size());
    } else {
        sector_out.fill(0);
    }
}

bool VfatMsdEmulator::is_firmware_file(const uint8_t* entry_name) const {
    // Перевірка розширення файлу (.BIN або .HEX)
    return (std::memcmp(&entry_name[8], "BIN", 3) == 0 ||
            std::memcmp(&entry_name[8], "HEX", 3) == 0);
}

bool VfatMsdEmulator::write_sector(uint32_t lba, std::span<const uint8_t, FAT_SECTOR_SIZE> sector_in) {
    // 1. Перехоплення запису в Root Directory
    if (lba >= ROOT_DIR_LBA && lba < DATA_START_LBA) {
        const auto* entries = reinterpret_cast<const FatDirectoryEntry*>(sector_in.data());
        size_t count = FAT_SECTOR_SIZE / sizeof(FatDirectoryEntry);

        for (size_t i = 0; i < count; ++i) {
            if (entries[i].filename[0] != 0x00 && entries[i].filename[0] != 0xE5) {
                if (is_firmware_file(entries[i].filename)) {
                    std::cout << "[MSD Drag-n-Drop] Виявлено копіювання файлу прошивки!\n";
                    is_flashing_active_ = true;
                    active_file_start_cluster_ = entries[i].start_cluster;

                    flash_state_.reset();
                    flash_state_.status = FlashStatus::Erasing;

                    // Ініціалізація SWD програматора
                    dap_handler_.connect_swd();
                    dap_handler_.target_halt();
                    dap_handler_.target_flash_unlock();
                }
            }
        }
        return true;
    }

    // 2. Перехоплення запису секторів у область даних (Data Area)
    if (lba >= DATA_START_LBA && is_flashing_active_) {
        uint32_t cluster_idx = (lba - DATA_START_LBA) / SECTORS_PER_CLUSTER;
        uint32_t target_address = flash_state_.flash_base_address + flash_state_.current_offset;

        // Посекторне стирання сторінок перед програмуванням (наприклад, сектори по 1 КБ / 4 КБ)
        if (target_address >= flash_state_.erased_up_to_address) {
            dap_handler_.target_flash_erase_sector(target_address);
            flash_state_.erased_up_to_address += 4096; // Додаємо розмір сектора Flash
        }

        // Програмування отриманих 512 байт у Flash цільового МК
        flash_state_.status = FlashStatus::Programming;
        if (dap_handler_.target_flash_program_page(target_address, sector_in)) {
            flash_state_.current_offset += FAT_SECTOR_SIZE;
            flash_state_.total_bytes_received += FAT_SECTOR_SIZE;
            std::cout << "[MSD Flash] Успішно записано 512 байт за адресою 0x" 
                      << std::hex << target_address << std::dec << "\n";
        } else {
            flash_state_.mark_error(0x01);
            std::cout << "[MSD Flash] Помилка запису у Flash!\n";
            return false;
        }

        // Завершення прошивки при поверненні в Idle стан
        if (flash_state_.current_offset >= 2048) { // Приклад фіксованого бінарника в прикладі
            flash_state_.status = FlashStatus::Completed;
            is_flashing_active_ = false;
            dap_handler_.target_reset_and_run();
            std::cout << "[MSD Drag-n-Drop] Прошивання цільового пристрою успішно завершено!\n";
        }
        return true;
    }

    return true;
}

bool VfatMsdEmulator::process_scsi_cbw(std::span<const uint8_t> cbw_data, 
                                        std::vector<uint8_t>& response_data, 
                                        Csw& csw_out) {
    if (cbw_data.size() < sizeof(Cbw)) return false;

    Cbw cbw{};
    std::memcpy(&cbw, cbw_data.data(), sizeof(Cbw));

    if (cbw.signature != 0x43425355) return false; // Signature "USBC"

    csw_out.signature = 0x53425355; // Signature "USBS"
    csw_out.tag = cbw.tag;
    csw_out.data_residue = 0;
    csw_out.status = 0; // Success

    uint8_t scsi_opcode = cbw.cb[0];
    response_data.clear();

    switch (scsi_opcode) {
        case 0x12: { // SCSI INQUIRY
            response_data.resize(36, 0);
            response_data[0] = 0x00; // Direct Access Block Device
            response_data[1] = 0x80; // Removable Media
            response_data[2] = 0x02; // ANSI SCSI-2 standard
            response_data[3] = 0x02; // Response data format
            response_data[4] = 31;   // Additional length

            std::memcpy(&response_data[8],  "STLink  ", 8);
            std::memcpy(&response_data[16], "V2.1 MSD Flash  ", 16);
            std::memcpy(&response_data[32], "1.00", 4);
            break;
        }
        case 0x25: { // SCSI READ CAPACITY (10)
            response_data.resize(8, 0);
            uint32_t last_lba = TOTAL_SECTORS - 1;
            uint32_t block_len = FAT_SECTOR_SIZE;

            // SCSI повертає значення у Big-Endian форматі
            response_data[0] = (last_lba >> 24) & 0xFF;
            response_data[1] = (last_lba >> 16) & 0xFF;
            response_data[2] = (last_lba >> 8) & 0xFF;
            response_data[3] = last_lba & 0xFF;

            response_data[4] = (block_len >> 24) & 0xFF;
            response_data[5] = (block_len >> 16) & 0xFF;
            response_data[6] = (block_len >> 8) & 0xFF;
            response_data[7] = block_len & 0xFF;
            break;
        }
        case 0x00: // TEST UNIT READY
        case 0x1A: // MODE SENSE (6)
            break;
        case 0x28: { // SCSI READ (10)
            uint32_t lba = (cbw.cb[2] << 24) | (cbw.cb[3] << 16) | (cbw.cb[4] << 8) | cbw.cb[5];
            uint16_t blocks = (cbw.cb[7] << 8) | cbw.cb[8];

            response_data.resize(blocks * FAT_SECTOR_SIZE);
            for (uint16_t b = 0; b < blocks; ++b) {
                std::span<uint8_t, FAT_SECTOR_SIZE> sector_span(
                    response_data.data() + b * FAT_SECTOR_SIZE, FAT_SECTOR_SIZE
                );
                read_sector(lba + b, sector_span);
            }
            break;
        }
        default:
            break;
    }
    return true;
}
