// Прочитати стан. Повертає true, якщо у NVS лежить чинний наш блоб.
static bool fastconn_load(fastconn_t *out)
{
    nvs_handle_t h;
    esp_err_t err = nvs_open(NVS_NS, NVS_READONLY, &h);
    if (err != ESP_OK) {
        // ESP_ERR_NVS_NOT_FOUND тут — норма для найпершого, чистого старту
        return false;
    }

    // Фаза 1: дізнаємося розмір збереженого блоба.
    size_t sz = 0;
    err = nvs_get_blob(h, NVS_KEY, NULL, &sz);
    if (err != ESP_OK || sz != sizeof(*out)) {
        nvs_close(h);
        return false;   // ключа немає або розмір не наш — формат чужий
    }

    // Фаза 2: читаємо самі дані.
    err = nvs_get_blob(h, NVS_KEY, out, &sz);
    nvs_close(h);
    if (err != ESP_OK) {
        return false;
    }

    // І остання перевірка чинності — мітка й версія формату.
    if (out->magic != FASTCONN_MAGIC || out->version != FASTCONN_VERSION) {
        ESP_LOGW(TAG, "blob magic/version mismatch — ignoring");
        return false;
    }
    return true;
}
