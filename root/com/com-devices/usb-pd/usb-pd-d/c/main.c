// callback: контролер віддав меню Source_Capabilities (масив PDO)
bool sink_negotiate(const pdo_t *pdo, uint8_t n) {
    const uint32_t v_want_mv = 20000;     // потрібні 20 В
    int best = -1;
    for (uint8_t i = 0; i < n; i++)       // перебрати меню
        if (pdo[i].type == PDO_FIXED &&
            pdo[i].voltage_mv <= v_want_mv &&            // не вище за стелю пристрою
            (best < 0 || pdo[i].voltage_mv > pdo[best].voltage_mv))
            best = i;                      // лишити найвищий придатний
    if (best < 0) return false;           // нічого не лягло → лишаємось на 5 В

    pd_send_request(best + 1, 3000);      // Request: профіль #(1-based), робочий струм 3 А
    if (pd_wait_accept(50) != PD_ACCEPT)  // джерело має відповісти Accept у межах таймауту
        return false;                     // відмова → контракт не укладено, 5 В
    pd_wait_event(PD_PS_RDY);             // PS_RDY: нова напруга на VBUS стоїть
    return true;                          // тепер на VBUS 20 В — контракт діє
}
