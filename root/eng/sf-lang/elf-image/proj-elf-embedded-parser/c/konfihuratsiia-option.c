#include <stdint.h>
#include <stdbool.h>

#define STM32_OPTBYTES_BASE 0x1FFFC000U

typedef struct {
    uint8_t rdp_level;
    uint8_t user_opt;
    uint16_t wrp_sectors;
} McuOptionBytes;

bool extract_option_bytes(const Elf32_Phdr* phdr_table, uint16_t phnum, 
                          const uint8_t* raw_bytes, McuOptionBytes* out_opt) {
    if (!phdr_table || !raw_bytes || !out_opt) return false;

    for (uint16_t i = 0; i < phnum; ++i) {
        if (phdr_table[i].p_paddr == STM32_OPTBYTES_BASE && phdr_table[i].p_filesz >= 4) {
            const uint8_t* opt_data = raw_bytes + phdr_table[i].p_offset;
            out_opt->rdp_level   = opt_data[0];
            out_opt->user_opt    = opt_data[1];
            out_opt->wrp_sectors = (uint16_t)(opt_data[2] | (opt_data[3] << 8));
            return true;
        }
    }
    return false; /* Секція Option Bytes не знайдена у двійковому образі */
}
