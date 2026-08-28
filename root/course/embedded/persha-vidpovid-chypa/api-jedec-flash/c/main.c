#include <stdint.h>
#include <stdbool.h>

#define JEDEC_CMD_READ_ID   0x9F

typedef struct {
    uint8_t  manufacturer_id;
    uint8_t  memory_type;
    uint8_t  capacity_id;
    uint32_t total_size_bytes;
    uint32_t sector_size_bytes;
    uint32_t page_size_bytes;
    uint32_t total_sectors;
    const char* vendor_name;
    bool     is_valid;
} jedec_flash_info_t;

const char* jedec_lookup_vendor(uint8_t mfg_id) {
    switch (mfg_id) {
        case 0xEF: return "Winbond";
        case 0xC2: return "Macronix";
        case 0xC8: return "GigaDevice";
        case 0x20: return "Micron/Numonyx";
        case 0x01: return "Spansion/Infineon";
        case 0xBF: return "Microchip/SST";
        case 0x9D: return "ISSI";
        case 0x85: return "Puya";
        case 0x68: return "Boya";
        case 0x5E: return "Zbit";
        default:   return "Unknown Vendor";
    }
}

jedec_flash_info_t jedec_decode_response(const uint8_t raw_id[3]) {
    jedec_flash_info_t info = {0};
    
    // Перевірка на фізичні дефекти ліній (обрив підтяжки або замикання на землю)
    if ((raw_id[0] == 0xFF && raw_id[1] == 0xFF && raw_id[2] == 0xFF) ||
        (raw_id[0] == 0x00 && raw_id[1] == 0x00 && raw_id[2] == 0x00)) {
        info.is_valid = false;
        info.vendor_name = "Bus Fault (0x00/0xFF)";
        return info;
    }
    
    info.manufacturer_id = raw_id[0];
    info.memory_type     = raw_id[1];
    info.capacity_id     = raw_id[2];
    info.vendor_name     = jedec_lookup_vendor(raw_id[0]);
    
    // Валідація підтримуваного діапазону ємностей (від 64 КБ до 64 МБ)
    if (info.capacity_id >= 0x10 && info.capacity_id <= 0x1A) {
        info.total_size_bytes  = 1UL << info.capacity_id;
        info.sector_size_bytes = 4096; // Стандартний розмір 4 КБ секторів
        info.page_size_bytes   = 256;  // Стандартний розмір сторінки 256 Б
        info.total_sectors     = info.total_size_bytes / info.sector_size_bytes;
        info.is_valid          = true;
    } else {
        info.total_size_bytes = 0;
        info.is_valid         = false;
    }
    
    return info;
}
