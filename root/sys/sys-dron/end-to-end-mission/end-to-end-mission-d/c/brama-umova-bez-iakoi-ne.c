// Кожна перевірка повертає true = «моя умова в нормі».
// Озброєння дозволене, лише якщо всі до єдиної повернули true.
bool arming_allowed(char *reason, size_t n) {
    if (!power_ok())        { snprintf(reason, n, "напруга поза межами");   return false; }
    if (!sensors_ok())      { snprintf(reason, n, "давач не калібрований");  return false; }
    if (!attitude_valid())  { snprintf(reason, n, "оцінка кута ще не збіглась"); return false; }
    if (failsafe_active())  { snprintf(reason, n, "активний failsafe");      return false; }
    return true;            // усі брами пройдено — озброєння дозволене
}

// Перехід у armed можливий ЛИШЕ через цю функцію — іншого шляху немає.
bool try_arm(void) {
    char why[48];
    if (!arming_allowed(why, sizeof why)) {
        gcs_send_text("ARM REJECTED: %s", why);  // скажи операторові, ЧОМУ
        return false;                            // лишаємось роззброєними
    }
    set_state(ST_ARMED);
    return true;
}
