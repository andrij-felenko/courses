// ── Стани приймача EPR (поверх уже готового SPR-стеку) ──────────────
typedef enum {
    ST_SPR,         // діє звичайний контракт, на VBUS безпечні 5 В
    ST_ENTERING,    // послано EPR_Mode(Enter), чекаємо Enter Succeeded
    ST_REQUESTING,  // режим є, просимо 48 В / AVS, чекаємо PS_RDY
    ST_EPR_ACTIVE,  // 48 В стоять, ключ замкнено, йде серцебиття
} epr_state_t;

static volatile epr_state_t g_state = ST_SPR;

// Спроба піднятися з готового SPR-контракту в режим EPR.
// Повертає true лише коли джерело підтвердило Enter Succeeded.
bool epr_try_enter(void) {
    // ПАСТКА №1: у EPR не можна входити «з нуля».
    // EPR_Mode — надбудова НАД наявним явним контрактом, не заміна йому.
    if (!spr_contract_active())        // ще нема навіть звичайного контракту?
        return false;                  // тоді й EPR просити нема з чого

    g_state = ST_ENTERING;
    pd_send_epr_mode(EPR_ENTER);       // «прошу увійти в розширений режим»

    // Джерело мусить підтвердити вхід у межах tEnterEPR (~450 мс). Воно ще й
    // опитає e-marker кабелю (чи тягне 50 В / 5 А?) — це його клопіт, ми чекаємо.
    if (!pd_wait_event_to(PD_EPR_ENTER_SUCCEEDED, 500)) {
        g_state = ST_SPR;              // Enter Failed або тиша → лишаємось на 5 В
        return false;
    }
    return true;                       // режим EPR є; високі профілі стали видні
}
