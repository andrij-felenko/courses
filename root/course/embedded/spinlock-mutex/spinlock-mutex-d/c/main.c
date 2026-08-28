static SemaphoreHandle_t flash_mutex;   // створити раз під час старту:
// flash_mutex = xSemaphoreCreateMutex();

void save_settings(const settings_t *s) {
    // чекати на замок до 100 мс; портить — засинаємо, а не крутимось
    if (xSemaphoreTake(flash_mutex, pdMS_TO_TICKS(100)) == pdTRUE) {
        flash_write_page(s);            // ДОВГО й блокувально — тут це дозволено
        xSemaphoreGive(flash_mutex);    // віддати замок: сплячий очікувач прокинеться
    } else {
        // за 100 мс не дочекались — замок досі чужий; обробити тайм-аут
    }
}
