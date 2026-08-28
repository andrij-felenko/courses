// Скопіювати серійник у буфер. Повертає true лише якщо запис валідний.
bool prov_get_serial(uint8_t out[8]) {
    if (!s_valid) return false;
    memcpy(out, s_record.serial, sizeof(s_record.serial));
    return true;
}

// Скопіювати MAC. Так само мовчить на невалідованому записі.
bool prov_get_mac(uint8_t out[6]) {
    if (!s_valid) return false;
    memcpy(out, s_record.mac, sizeof(s_record.mac));
    return true;
}

// Дістати калібрувальний коефіцієнт #i. Поза валідним записом — false.
bool prov_get_cal(int i, float *out) {
    if (!s_valid || i < 0 || i >= PROV_CAL_COEFFS) return false;
    *out = s_record.cal[i];
    return true;
}
