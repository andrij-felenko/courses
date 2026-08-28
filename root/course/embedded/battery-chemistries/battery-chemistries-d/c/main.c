// Рішення про дозвіл і струм заряду за температурою комірки.
// Температура — з давача НА комірці (не поряд із платою: різниця
// в кілька градусів на морозі вирішальна).
typedef enum { CHG_BLOCK, CHG_TRICKLE, CHG_FULL } charge_mode_t;

charge_mode_t charge_policy(float t_cell_c) {
    if (t_cell_c < 0.0f)  return CHG_BLOCK;    // мороз: заряд заборонено
    if (t_cell_c < 10.0f) return CHG_TRICKLE;  // прохолодно: лише крихітний струм
    if (t_cell_c > 45.0f) return CHG_BLOCK;    // спека: заряд теж стоп
    return CHG_FULL;                            // безпечне вікно
}

// У циклі заряду:
switch (charge_policy(read_cell_temp())) {
    case CHG_BLOCK:   set_charge_current_ma(0);       break;
    case CHG_TRICKLE: set_charge_current_ma(50);      break;  // ~0.02C, безпечно й на холоді
    case CHG_FULL:    set_charge_current_ma(i_full);  break;
}
