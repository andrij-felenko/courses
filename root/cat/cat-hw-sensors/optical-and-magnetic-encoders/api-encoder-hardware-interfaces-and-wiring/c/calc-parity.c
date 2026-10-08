#include <stdint.h>
#include <stdbool.h>

#define REG_ZERO_POS   0x0001
#define REG_AGC        0x3FFD
#define CMD_READ_FLAG  0x4000

static uint16_t calc_parity(uint16_t frame) {
    uint16_t count = 0;
    for (int i = 0; i < 16; i++) {
        if (frame & (1 << i)) count++;
    }
    return (count % 2 != 0) ? (frame | 0x8000) : frame;
}

bool encoder_set_zero_offset(uint16_t raw_offset, uint16_t (*spi_transfer)(uint16_t)) {
    uint16_t cmd_zero = calc_parity(REG_ZERO_POS);
    uint16_t val_zero = calc_parity(raw_offset & 0x3FFF);
    
    spi_transfer(cmd_zero);
    spi_transfer(val_zero);
    
    uint16_t cmd_agc = calc_parity(REG_AGC | CMD_READ_FLAG);
    uint16_t agc_val = spi_transfer(cmd_agc) & 0x00FF;
    
    return (agc_val >= 10 && agc_val <= 245);
}
