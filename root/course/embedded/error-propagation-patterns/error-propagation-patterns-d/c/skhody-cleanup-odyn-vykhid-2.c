esp_err_t process(void) {
    esp_err_t ret = ESP_OK;
    uint8_t  *buf = NULL;

    port_t *p = port_open();
    if (p == NULL) return ESP_FAIL;     // ще нічого не взяли — звичайний return

    buf = malloc(1024);
    if (buf == NULL) { ret = ESP_ERR_NO_MEM; goto cleanup; }

    ret = port_read(p, buf, 1024);
    if (ret != ESP_OK) goto cleanup;    // збій — туди ж, де й усі

    // ... тут далі робота з buf і p ...

cleanup:
    free(buf);                          // звільнення — РІВНО ОДИН раз
    port_close(p);                      // у зворотному порядку до взяття
    return ret;
}
