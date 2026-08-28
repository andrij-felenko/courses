#define SET_TIMEOUT_MS  1000
#define SET_RETRIES     3

bool param_set_blocking(const char *id, float want, uint8_t type) {
    for (int attempt = 0; attempt < SET_RETRIES; attempt++) {
        send_param_set(id, want, type);
        uint32_t t0 = now_ms();
        while (now_ms() - t0 < SET_TIMEOUT_MS) {
            mavlink_param_value_t pv;
            if (recv_param_value(&pv) && name_eq(pv.param_id, id)) {
                return float_eq(pv.param_value, want);   // борт підтвердив САМЕ це
            }
        }
        // тиша → пакет загубився, шлемо PARAM_SET ще раз
    }
    return false;   // борт так і не підтвердив — не вважаємо записаним
}
