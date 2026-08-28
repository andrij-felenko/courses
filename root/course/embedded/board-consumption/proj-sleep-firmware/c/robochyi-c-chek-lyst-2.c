// ── Крок 1: явно приспати зовнішній давач по шині ─────────────────────────
// Поки I2C ще живий і гілка ще під напругою — інакше команду не віддати.
static void sensor_power_down(void)
{
    uint8_t cmd[2] = { SENSOR_REG_CTRL, SENSOR_MODE_SLEEP };
    esp_err_t err = i2c_master_write_to_device(
        I2C_PORT, SENSOR_I2C_ADDR, cmd, sizeof(cmd),
        pdMS_TO_TICKS(50));
    if (err != ESP_OK) {
        // Давач не відповів — це саме по собі проблема бюджету:
        // не приспаний давач з'їсть сон. Логуємо, а не мовчимо.
        ESP_LOGW(TAG, "davach ne zasnuv: %s", esp_err_to_name(err));
    }
    i2c_driver_delete(I2C_PORT);   // звільнити драйвер шини
}
