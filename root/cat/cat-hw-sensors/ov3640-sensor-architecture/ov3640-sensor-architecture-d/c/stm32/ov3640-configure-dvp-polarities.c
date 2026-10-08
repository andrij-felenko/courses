#include <stdint.h>
#include <stdbool.h>

// Структура полярностей сигналів DVP
typedef struct {
    bool pclk_rising_edge;
    bool href_active_high;
    bool vsync_active_high;
} dvp_polarity_cfg_t;

// Низькорівневий запис через SCCB
extern bool ov3640_write_bank_reg(uint8_t bank, uint8_t reg, uint8_t val);

// Налаштування полярностей синхронізації у банку системного контролю OV3640
bool ov3640_configure_dvp_polarities(const dvp_polarity_cfg_t *cfg) {
    uint8_t reg_val = 0x00;
    
    if (cfg->pclk_rising_edge) {
        reg_val |= (1 << 4); // Bit 4: PCLK polarity (1 = rising, 0 = falling)
    }
    if (cfg->href_active_high) {
        reg_val |= (1 << 3); // Bit 3: HREF polarity (1 = high active)
    }
    if (cfg->vsync_active_high) {
        reg_val |= (1 << 2); // Bit 2: VSYNC polarity (1 = high active)
    }
    
    // Запис у регістр 0x11 банку 0 (System Control)
    return ov3640_write_bank_reg(0x00, 0x11, reg_val);
}
