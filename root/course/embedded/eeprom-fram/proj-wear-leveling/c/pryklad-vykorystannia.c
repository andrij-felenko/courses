static wl_ring_t g_ring;

void app_init(void) {
    wl_mount(&g_ring);                 // один раз при старті: знайти голову
}

// Збільшити лічильник напрацювання на 1 і зберегти (переживе вимкнення й знос).
void bump_run_counter(void) {
    uint8_t data[WL_DATA_LEN] = {0};
    uint32_t count = 0;

    if (wl_get(&g_ring, data)) {       // прочитати поточне значення (якщо є)
        memcpy(&count, data, sizeof(count));
    }
    count++;

    memset(data, 0, sizeof(data));
    memcpy(data, &count, sizeof(count));
    wl_put(&g_ring, data);             // записати нове значення в наступний слот
}
