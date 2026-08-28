// Округлити бажану напругу до сітки AVS (крок 100 мВ) і затиснути в [15..48] В.
static uint32_t avs_round_mv(uint32_t want_mv) {
    if (want_mv < 15000) want_mv = 15000;      // нижня межа AVS
    if (want_mv > 48000) want_mv = 48000;      // стеля EPR — і дотикової безпеки
    return ((want_mv + 50) / 100) * 100;       // до найближчих 100 мВ
}

// Домовитись про робочу напругу вже в режимі EPR і замкнути ключ.
// want_mv == 0  → взяти фіксовані 48 В (максимум); інакше — AVS під потребу.
bool epr_negotiate_voltage(uint32_t want_mv, uint32_t load_ma) {
    if (g_state != ST_ENTERING && g_state != ST_EPR_ACTIVE)
        return false;                          // без Enter Succeeded просити нема що
    g_state = ST_REQUESTING;

    pdo_t caps[13];                            // розширене меню довше за SPR-ове
    uint8_t n = pd_get_epr_source_caps(caps);  // 5/9/15/20 + 28/36/48 + рядок AVS

    if (want_mv == 0) {                        // хочемо стелю — шукаємо фіксовані 48 В
        int idx = epr_find_fixed(caps, n, 48000);
        if (idx < 0) return false;             // джерело не тягне 48 В
        pd_send_epr_request_fixed(idx, load_ma);
    } else {                                   // хочемо конкретну напругу — через AVS
        int idx = epr_find_avs(caps, n);
        if (idx < 0) return false;             // джерело не має AVS-рядка
        pd_send_epr_request_avs(idx, avs_round_mv(want_mv), load_ma);
    }

    if (pd_wait_accept(50) != PD_ACCEPT)       // джерело погодилось?
        return false;                          // відмова → контракту нема, 5 В лишаються
    pd_wait_event(PD_PS_RDY);                  // чекаємо: нова напруга на VBUS СТОЇТЬ

    gate_enable();                             // ПАСТКА №2 позаду: ключ — лише ТЕПЕР
    g_state = ST_EPR_ACTIVE;
    epr_keepalive_start();                     // запустити серцебиття (нижче)
    return true;
}
