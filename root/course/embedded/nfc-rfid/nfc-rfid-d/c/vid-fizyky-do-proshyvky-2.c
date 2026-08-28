static uint8_t last_uid[10];
static uint8_t last_len = 0;

void access_control_poll(void)
{
    uint8_t uid[10];
    uint8_t len = nfc_read_uid(uid);

    if (len == 0) {
        last_len = 0;                // поле порожнє — скидаємо пам'ять
        return;
    }

    // Та сама картка досі в полі? — не реагуємо повторно (антидребезг).
    bool same = (len == last_len);
    for (uint8_t i = 0; same && i < len; i++)
        if (uid[i] != last_uid[i]) same = false;
    if (same) return;

    // Нова картка — обробляємо один раз.
    for (uint8_t i = 0; i < len; i++) last_uid[i] = uid[i];
    last_len = len;

    if (access_uid_is_allowed(uid, len))
        door_unlock();
    else
        beep_denied();
}
