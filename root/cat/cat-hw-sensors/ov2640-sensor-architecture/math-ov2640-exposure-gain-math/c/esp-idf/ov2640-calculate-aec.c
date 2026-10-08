#include <stdint.h>
#include <stdbool.h>

// Структура регістрових значень AEC для OV2640
typedef struct {
    uint8_t reg04; // Містить AEC[1:0] та AEC[15:10]
    uint8_t aec;   // Містить AEC[9:2]
    uint16_t dummy_lines;
} ov2640_aec_regs_t;

// Розрахунок регістрів експозиції OV2640
bool ov2640_calculate_aec(uint32_t target_exp_us, uint32_t f_pclk_hz, 
                         uint16_t n_pixel, uint16_t n_line, 
                         ov2640_aec_regs_t *out_regs) {
    if (f_pclk_hz == 0 || n_pixel == 0 || out_regs == NULL) return false;

    // Тривалість одного рядка у наносекундах для збереження точності
    uint64_t t_line_ns = ((uint64_t)n_pixel * 1000000000ULL) / f_pclk_hz;
    uint32_t aec_lines = (uint32_t)(((uint64_t)target_exp_us * 1000000ULL) / t_line_ns);

    uint16_t max_lines_standard = (n_line > 16) ? (n_line - 16) : n_line;

    if (aec_lines > max_lines_standard) {
        out_regs->dummy_lines = aec_lines - max_lines_standard;
    } else {
        out_regs->dummy_lines = 0;
    }

    // Формування бітових полів регістрів OV2640
    // AEC[1:0] -> REG04[1:0], AEC[9:2] -> AEC[7:0], AEC[15:10] -> REG04[7:2]
    uint8_t aec_1_0 = aec_lines & 0x03;
    uint8_t aec_9_2 = (aec_lines >> 2) & 0xFF;
    uint8_t aec_15_10 = (aec_lines >> 10) & 0x3F;

    out_regs->reg04 = (aec_15_10 << 2) | aec_1_0;
    out_regs->aec = aec_9_2;

    return true;
}
