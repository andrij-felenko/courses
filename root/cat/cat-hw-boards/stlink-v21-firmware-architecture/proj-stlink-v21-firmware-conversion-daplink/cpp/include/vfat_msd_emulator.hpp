#ifndef VFAT_MSD_EMULATOR_HPP
#define VFAT_MSD_EMULATOR_HPP

#include <cstdint>
#include <cstddef>
#include <array>
#include <vector>
#include <span>
#include <string_view>
#include <memory>
#include "cmsis_dap_handler.hpp"

constexpr size_t FAT_SECTOR_SIZE = 512;
constexpr uint32_t DEFAULT_FLASH_BASE_ADDR = 0x08000000; // Базова адреса Flash STM32

// Статуси автомата станів Drag-and-Drop прошивача
enum class FlashStatus : uint8_t {
    Idle,
    Erasing,
    Programming,
    Verifying,
    Completed,
    Error
};

// Скінченний автомат стану прошивання через віртуальний диск
struct FlashProgressState {
    FlashStatus status{FlashStatus::Idle};
    uint32_t flash_base_address{DEFAULT_FLASH_BASE_ADDR};
    uint32_t current_offset{0};
    uint32_t total_bytes_received{0};
    uint32_t erased_up_to_address{DEFAULT_FLASH_BASE_ADDR};
    uint8_t error_code{0};

    void reset() {
        status = FlashStatus::Idle;
        current_offset = 0;
        total_bytes_received = 0;
        erased_up_to_address = flash_base_address;
        error_code = 0;
    }

    void mark_error(uint8_t code) {
        status = FlashStatus::Error;
        error_code = code;
    }

    [[nodiscard]] bool is_active() const {
        return status == FlashStatus::Erasing || status == FlashStatus::Programming;
    }
};

// Структури підтримуваного протоколу USB Mass Storage (SCSI Command / Status Wrapper)
#pragma pack(push, 1)
struct Cbw {
    uint32_t signature;          // 0x43425355 ("USBC")
    uint32_t tag;
    uint32_t data_transfer_length;
    uint8_t  flags;
    uint8_t  lun;
    uint8_t  cb_length;
    uint8_t  cb[16];
};

struct Csw {
    uint32_t signature;          // 0x53425355 ("USBS")
    uint32_t tag;
    uint32_t data_residue;
    uint8_t  status;             // 0: Success, 1: Failed, 2: Phase Error
};

// Структура записи FAT directory entry (32 байти)
struct FatDirectoryEntry {
    uint8_t  filename[11];      // 8.3 формат
    uint8_t  attributes;        // 0x20 = ARCHIVE, 0x08 = VOLUME_ID
    uint8_t  reserved[10];
    uint16_t time_stamp;
    uint16_t date_stamp;
    uint16_t start_cluster;
    uint32_t file_size;
};
#pragma pack(pop)

// Клас емулятора накопичувача USB MSD та віртуальної FAT16
class VfatMsdEmulator {
public:
    explicit VfatMsdEmulator(CmsisDapHandler& dap_handler);
    ~VfatMsdEmulator() = default;

    // Зчитування сектора віртуального диска по LBA
    void read_sector(uint32_t lba, std::span<uint8_t, FAT_SECTOR_SIZE> sector_out);

    // Запис сектора з перехопленням операцій копіювання файлу прошивки
    bool write_sector(uint32_t lba, std::span<const uint8_t, FAT_SECTOR_SIZE> sector_in);

    // Обробка вхідного пакету SCSI Command Block Wrapper (CBW)
    bool process_scsi_cbw(std::span<const uint8_t> cbw_data, 
                          std::vector<uint8_t>& response_data, 
                          Csw& csw_out);

    [[nodiscard]] const FlashProgressState& get_flash_state() const { return flash_state_; }

private:
    CmsisDapHandler& dap_handler_;
    FlashProgressState flash_state_;

    // Параметри VFAT диска
    static constexpr uint32_t TOTAL_SECTORS = 65536;    // 32 МБ віртуальний диск
    static constexpr uint16_t RESERVED_SECTORS = 1;
    static constexpr uint8_t  SECTORS_PER_CLUSTER = 8;  // Кластер 4 КБ
    static constexpr uint8_t  NUMBER_OF_FATS = 2;
    static constexpr uint16_t ROOT_DIR_ENTRIES = 512;   // 32 сектори під каталог
    static constexpr uint16_t SECTORS_PER_FAT = 64;

    static constexpr uint32_t FAT1_LBA = RESERVED_SECTORS;
    static constexpr uint32_t FAT2_LBA = FAT1_LBA + SECTORS_PER_FAT;
    static constexpr uint32_t ROOT_DIR_LBA = FAT2_LBA + SECTORS_PER_FAT;
    static constexpr uint32_t DATA_START_LBA = ROOT_DIR_LBA + (ROOT_DIR_ENTRIES * 32 / FAT_SECTOR_SIZE);

    // Збережений файл прошивки під час Drag-and-Drop
    bool is_flashing_active_{false};
    uint32_t active_file_start_cluster_{0};

    // Генератори секторів VFAT
    void generate_boot_sector(std::span<uint8_t, FAT_SECTOR_SIZE> sector);
    void generate_fat_sector(uint32_t lba, std::span<uint8_t, FAT_SECTOR_SIZE> sector);
    void generate_root_dir_sector(uint32_t lba, std::span<uint8_t, FAT_SECTOR_SIZE> sector);

    // Перевірка, чи є створений файл бінарним білдом прошивки (.BIN / .HEX)
    bool is_firmware_file(const uint8_t* entry_name) const;
};

#endif // VFAT_MSD_EMULATOR_HPP
