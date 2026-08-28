// без guard clause: логіка тоне у вкладеності
esp_err_t handle(const msg_t *m) {
    if (m != NULL) {
        if (m->len <= MAX) {
            if (m->crc_ok) {
                /* ...справжня робота захована на три рівні вглиб... */
                return ESP_OK;
            }
        }
    }
    return ESP_ERR_INVALID_ARG;
}

// з guard clause: застави спереду, тіло пласке
esp_err_t handle(const msg_t *m) {
    if (m == NULL)        return ESP_ERR_INVALID_ARG;
    if (m->len > MAX)     return ESP_ERR_INVALID_SIZE;
    if (!m->crc_ok)       return ESP_ERR_INVALID_CRC;
    /* ...справжня робота, дані вже чисті... */
    return ESP_OK;
}
