typedef struct {
    float eirp_dbm;      // легальний EIRP після обрізання
    float p_rx_dbm;      // потужність на вході приймача
    float s_rx_dbm;      // поріг чутливості
    float margin_db;     // запас лінії = p_rx − s_rx
    bool  eirp_clipped;  // true, якщо запит на потужність зрізала стеля
} link_result_t;

// Параметри лінії — зібрані в одну структуру, щоб виклик читався.
typedef struct {
    float p_tx_dbm;        // потужність передавача, дБм
    float g_tx_dbi;        // підсилення TX-антени, дБі
    float l_cable_tx_db;   // втрати кабелю до TX-антени, дБ
    float d_m;             // відстань, метри
    float f_mhz;           // частота, МГц
    float l_misc_db;       // інші втрати шляху (стіни, дощ...), дБ
    float g_rx_dbi;        // підсилення RX-антени, дБі
    float l_cable_rx_db;   // втрати кабелю RX, дБ
    float b_hz;            // смуга приймача, Гц
    float nf_db;           // коефіцієнт шуму приймача, дБ
    float snr_min_db;      // потрібний SNR модуляції, дБ
    rf_region_t region;    // регуляторний регіон (стеля EIRP)
} link_params_t;

// Повний потермовий бюджет із легальним обрізанням EIRP.
link_result_t link_budget(const link_params_t *p) {
    link_result_t r;
    r.eirp_dbm = eirp_clipped_dbm(p->p_tx_dbm, p->g_tx_dbi,
                                  p->l_cable_tx_db, p->region,
                                  &r.eirp_clipped);
    float l_path = fspl_db(p->d_m, p->f_mhz) + p->l_misc_db;
    r.p_rx_dbm  = r.eirp_dbm - l_path + p->g_rx_dbi - p->l_cable_rx_db;
    r.s_rx_dbm  = sensitivity_dbm(p->b_hz, p->nf_db, p->snr_min_db);
    r.margin_db = r.p_rx_dbm - r.s_rx_dbm;
    return r;
}
