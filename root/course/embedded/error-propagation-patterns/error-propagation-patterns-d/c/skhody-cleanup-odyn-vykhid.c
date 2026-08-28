esp_err_t process(void) {
    port_t *p = port_open();
    if (p == NULL) return ESP_FAIL;

    uint8_t *buf = malloc(1024);
    if (buf == NULL) {
        port_close(p);                  // звільнити те, що вже взяли
        return ESP_ERR_NO_MEM;
    }

    esp_err_t err = port_read(p, buf, 1024);
    if (err != ESP_OK) {
        free(buf);                      // і знову...
        port_close(p);                  // ...повторюємо звільнення
        return err;
    }

    free(buf);                          // і на щасливому шляху теж
    port_close(p);
    return ESP_OK;
}
