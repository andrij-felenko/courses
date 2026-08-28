// Дві кнопки: обидві натиснуті у вікні 500 мс, і обидві відпущені перед новим пуском.
bool two_hand_ok(void) {
    static uint16_t l_ms = 0, r_ms = 0;   // як довго кожна тримається, мс
    static bool armed = true;             // чи відпускали обидві після минулого пуску
    bool l = button_l(), r = button_r();

    l_ms = l ? (uint16_t)(l_ms + 1) : 0;
    r_ms = r ? (uint16_t)(r_ms + 1) : 0;

    if (!l && !r) armed = true;           // обидві відпущено — знову дозволено

    if (armed && l && r && l_ms < 500 && r_ms < 500) {
        armed = false;                    // до наступного відпускання — блок
        return true;                      // одночасне свіже натискання
    }
    return false;
}
