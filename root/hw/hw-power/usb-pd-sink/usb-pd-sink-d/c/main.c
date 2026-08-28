// callback: контролер віддав меню Source_Capabilities (масив PDO)
bool sink_pick_profile(const pdo_t *pdo, uint8_t n) {
    const uint32_t v_max_mv = 12000;      // стеля пристрою: понад 12 В брати НЕ можна
    int best = -1;
    for (uint8_t i = 0; i < n; i++)        // перебрати всі рядки меню
        if (pdo[i].type == PDO_FIXED &&
            pdo[i].voltage_mv <= v_max_mv &&                 // не вище за стелю
            (best < 0 || pdo[i].voltage_mv > pdo[best].voltage_mv))
            best = i;                       // лишити найвищий придатний
    if (best < 0) return false;             // нічого не лягло → лишаємось на 5 В

    pd_send_request(best + 1, 2000);        // Request: профіль #(1-based), робочий струм 2 А
    if (pd_wait_accept(50) != PD_ACCEPT)    // джерело має відповісти Accept у межах таймауту
        return false;                       // відмова → контракту нема, на шині 5 В
    pd_wait_event(PD_PS_RDY);               // PS_RDY: нова напруга на VBUS стоїть
    gate_enable();                          // ЛИШЕ ТЕПЕР замкнути ключ на навантаження
    return true;                            // контракт діє, 12 В дійшли до пристрою
}
