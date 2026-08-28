// bit i у arming_check_mask == 1 → перевірку CHECKS[i] увімкнено.
bool try_arm(uint32_t arming_check_mask) {
    if (!arm_command_present())              // немає свідомої команди — не арматимемо
        return false;

    char reason[50];
    for (int i = 0; i < (int)(sizeof(CHECKS) / sizeof(CHECKS[0])); i++) {
        bool enabled = CHECKS[i].mandatory ||       // обов'язкову НЕ обійти бітом
                       (arming_check_mask & (1u << i));
        if (enabled && !CHECKS[i].check(reason, sizeof(reason))) {
            gcs_send_text("PreArm: %s", reason);     // сказати ЧОМУ не пускає
            return false;                            // перша ж причина — і стоп
        }
    }
    armed = true;                            // усі пройшли → ворота відчинено
    gcs_send_text("Armed");
    return true;
}
