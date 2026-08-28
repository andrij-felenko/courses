// Власний обробник: фіксуємо контекст, ТОДІ зупиняємось
void app_assert_failed(const char *file, int line, const char *expr) {
    // 1) зберегти у місце, що переживе reset (журнал у Flash / RTC-пам'ять)
    log_to_flash("ASSERT %s:%d  (%s)", file, line, expr);
    // 2) у консоль — для того, хто дивиться зараз
    ESP_LOGE("ASSERT", "%s:%d  expr: %s", file, line, expr);
    // 3) лише тепер — паніка з відомою причиною
    esp_system_abort("assert failed");
}

// Перевизначаємо стандартний assert на свій обробник
#ifdef NDEBUG
  #define APP_ASSERT(expr) ((void)0)
#else
  #define APP_ASSERT(expr) \
      ((expr) ? (void)0 : app_assert_failed(__FILE__, __LINE__, #expr))
#endif
