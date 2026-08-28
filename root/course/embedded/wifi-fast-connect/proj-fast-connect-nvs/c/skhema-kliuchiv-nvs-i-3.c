// Має викликатися один раз на старті, до будь-якої роботи з NVS.
static void fastconn_nvs_init(void)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES ||
        err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());   // розділ застарів/побився — стерти
        err = nvs_flash_init();               // і спробувати знову на чистому
    }
    ESP_ERROR_CHECK(err);
}
