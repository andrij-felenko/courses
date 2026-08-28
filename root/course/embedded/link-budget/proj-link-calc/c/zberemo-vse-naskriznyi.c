#include <stdio.h>

int main(void) {
    // ── Проєктний режим: чи полетить ця лінія? ───────────────────────────
    link_params_t link = {
        .p_tx_dbm = 14.0f, .g_tx_dbi = 5.0f, .l_cable_tx_db = 1.0f,
        .d_m = 40.0f, .f_mhz = 2450.0f, .l_misc_db = 8.0f,
        .g_rx_dbi = 2.0f, .l_cable_rx_db = 0.5f,
        .b_hz = 1.0e6f, .nf_db = 8.0f, .snr_min_db = 17.0f,
        .region = REGION_ETSI_2G4,
    };
    link_result_t r = link_budget(&link);

    printf("EIRP   = %+.1f дБм%s\n", r.eirp_dbm,
           r.eirp_clipped ? "  (ЗРІЗАНО стелею!)" : "");
    printf("P_rx   = %+.1f дБм\n", r.p_rx_dbm);
    printf("S_rx   = %+.1f дБм\n", r.s_rx_dbm);
    printf("запас  = %.1f дБ  → доступність ~%.1f%%\n",
           r.margin_db, 100.0f * availability_from_margin(r.margin_db));
    // → EIRP +18.0; P_rx −60.8; S_rx −89.0; запас 28.2 → доступність ~99.8%
    return 0;
}

// ── Польовий режим: рішення автономного апарата за виміряним RSSI ─────────
typedef enum { LINK_SOLID, LINK_MARGINAL, LINK_LOST } link_state_t;

// Викликати щоразу, коли прийшов пакет: rssi — з радіочипа, s_rx — з розрахунку.
link_state_t assess_link(float rssi_dbm, float s_rx_dbm) {
    float margin = margin_from_rssi(rssi_dbm, s_rx_dbm);
    float avail  = availability_from_margin(margin);
    if (avail >= 0.99f)  return LINK_SOLID;      // ≥ 20 дБ запасу — летимо далі
    if (avail >= 0.90f)  return LINK_MARGINAL;   // 10..20 дБ — обережно, ближче
    return LINK_LOST;                            // < 10 дБ — розворот на базу
}
