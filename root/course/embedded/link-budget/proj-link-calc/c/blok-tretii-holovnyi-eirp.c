typedef enum {
    REGION_ETSI_2G4 = 0,   // Європа, 2.4 ГГц: EIRP ≤ +20 дБм
    REGION_FCC_2G4  = 1,   // США, 2.4 ГГц:   EIRP ≤ +36 дБм (базово)
    REGION_NONE     = 2,   // без обмеження (стенд, лабораторія)
} rf_region_t;

// Регуляторна стеля EIRP для смуги 2.4 ГГц, дБм.
static float eirp_ceiling_dbm(rf_region_t reg) {
    switch (reg) {
        case REGION_ETSI_2G4: return 20.0f;
        case REGION_FCC_2G4:  return 36.0f;
        default:              return INFINITY;   // без стелі
    }
}

// EIRP після згортання TX-сторони, ОБРІЗАНИЙ до легальної межі.
// Повертає легальний EIRP і (через прапорець) сигналізує, що ми впёрлись у стелю.
static float eirp_clipped_dbm(float p_tx_dbm, float g_tx_dbi,
                              float l_cable_tx_db, rf_region_t reg,
                              bool *was_clipped) {
    float eirp = p_tx_dbm - l_cable_tx_db + g_tx_dbi;
    float ceil = eirp_ceiling_dbm(reg);
    if (eirp > ceil) {
        if (was_clipped) *was_clipped = true;
        return ceil;                 // закон переміг — світимо не більше стелі
    }
    if (was_clipped) *was_clipped = false;
    return eirp;
}
