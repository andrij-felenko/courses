// НЕПРАВИЛЬНО: використання настінного часу для таймаутів
uint32_t deadline = get_wall_time_seconds() + 5; // Таймаут 5 секунд

send_request_to_modem();

while (get_wall_time_seconds() < deadline) {
    if (check_modem_response()) {
        return STATUS_OK;
    }
    vTaskDelay(pdMS_TO_TICKS(10));
}
// Якщо час перевели назад — цикл крутитиметься не 5 секунд, а годинами!
