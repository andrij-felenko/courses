typedef enum {
    ESC_NORMAL = 0,     // усе гаразд
    ESC_SAFE_MODE,      // зайшли в safe mode
    ESC_CONFIG_ROLLED,  // конфіг уже відкочено
    ESC_FW_ROLLED,      // прошивку вже відкочено — далі тільки кликати на поміч
} esc_level_t;

static esc_level_t esc_load(void) {
    nvs_handle_t h;
    uint8_t v = ESC_NORMAL;
    if (nvs_open("reboot", NVS_READONLY, &h) == ESP_OK) {
        nvs_get_u8(h, "esc", &v);     // нема ключа → лишається ESC_NORMAL
        nvs_close(h);
    }
    return (esc_level_t)v;
}

static void esc_store(esc_level_t level) {   // ТІЛЬКИ в мить переходу — щадимо Flash
    nvs_handle_t h;
    if (nvs_open("reboot", NVS_READWRITE, &h) == ESP_OK) {
        nvs_set_u8(h, "esc", (uint8_t)level);
        nvs_commit(h);
        nvs_close(h);
    }
}
