static bool s_armed = false;

// Спроба озброїтися. Обидві застави мусять пропустити.
bool try_arm(bool operator_requested) {
    // Застава 2: чи цього СВІДОМО хтось захотів (стік/кнопка/вимикач)?
    if (!operator_requested)         return false;
    if (!safety_switch_pressed())    return false;   // апаратний запобіжник

    // Застава 1: чи система ПРИДАТНА (усі передпольотні перевірки)?
    const char *why = prearm_first_failure();
    if (why != nullptr) {
        // Відмова — не попередження: лишаємось обеззброєними, причина названа.
        return false;                // s_armed НЕ змінюємо
    }

    s_armed = true;                  // єдине місце, де апарат стає озброєним
    motors_enable();                 // тільки тепер двигуни можуть крутитися
    gcs_send_text("Armed");
    return true;
}

bool is_armed() { return s_armed; }
