void app_main(void) {
  gpio_config_t io = {
      .pin_bit_mask = (1ULL << PIN_CLK) | (1ULL << PIN_RST) | (1ULL << PIN_DAT),
      .mode = GPIO_MODE_OUTPUT,          // напрям DAT далі міняємо на льоту
      .pull_up_en = GPIO_PULLUP_DISABLE,
      .pull_down_en = GPIO_PULLDOWN_DISABLE,
      .intr_type = GPIO_INTR_DISABLE,
  };
  ESP_ERROR_CHECK(gpio_config(&io));
  gpio_set_level(PIN_RST, 0);            // сеанс закритий, поки не почали

  ds_write_protect_off();                // пустити годинник, якщо стоїть
  ds_clock_start();
  ds_write(REG_WP, 0x80);

  // Виставити час ОДИН раз на свіжій мікросхемі — розкоментуйте, прошийте,
  // тоді закоментуйте назад: інакше час скидатиметься при кожному старті.
  // struct Clock init = { 30, 47, 10, 4, 7, 5, 26 };
  // ds_set_time(&init);

  while (true) {
    struct Clock now;
    ds_read_burst(&now);
    ESP_LOGI(TAG, "20%02u-%02u-%02u %02u:%02u:%02u  (дн.тижня %u)",
             now.year, now.month, now.date, now.hour, now.min, now.sec, now.dow);
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}
