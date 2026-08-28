int64_t start = esp_timer_get_time();
bool got = false;

while (esp_timer_get_time() - start < 2000000LL) {  // ждемо щонайбільше 2 с
    if (data_ready()) { got = true; break; }
    vTaskDelay(1);                        // не тримаємо ядро мертвою петлею
}
if (!got) {
    ESP_LOGW(TAG, "тайм-аут: подія не настала за 2 с");
}
