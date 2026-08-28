static const fd_config_t CFG_CELL_TEMP = {
    .min = -40.0f, .max = 125.0f, .max_step = 4.0f, .timeout_ms = 500u,
    .eps = 0.1f, .stuck_limit = 20u, .trip_count = 3u, .heal_count = 30u,
};
static fd_channel_t cell_temp[4];    // 4 канали, ОДИН спільний конфіг

void cells_init(void) {
    for (int i = 0; i < 4; i++) fd_init(&cell_temp[i], &CFG_CELL_TEMP);
}

void on_cell_temps(const float t[4], uint32_t now_ms) {
    int healthy = 0;
    for (int i = 0; i < 4; i++)
        if (fd_update(&cell_temp[i], t[i], now_ms) == FD_TRUST) healthy++;
    // Над модулем — логіка системи: скільки каналів треба для безпеки.
    if (healthy < 2) enter_safe_mode();       // забагато сліпих термісторів
}
