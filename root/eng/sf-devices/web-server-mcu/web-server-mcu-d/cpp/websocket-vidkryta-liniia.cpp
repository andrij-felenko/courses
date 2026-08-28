// WebSocket-хендлер: ловить кадр від браузера й відповідає.
static esp_err_t ws_handler(httpd_req_t *req)
{
    if (req->method == HTTP_GET) return ESP_OK;   // це саме рукостискання — пропускаємо

    httpd_ws_frame_t frame = { .type = HTTPD_WS_TYPE_TEXT };
    httpd_ws_recv_frame(req, &frame, 0);          // спершу дізнаємось довжину
    // ... виділити буфер на frame.len, дочитати кадр, обробити ...
    return ESP_OK;
}

// Штовхнути свіже показання ВСІМ підключеним клієнтам (з іншої задачі).
void ws_push_temperature(httpd_handle_t server, int fd, float t)
{
    char msg[32];
    snprintf(msg, sizeof(msg), "{\"temp\":%.1f}", t);
    httpd_ws_frame_t frame = {
        .type = HTTPD_WS_TYPE_TEXT,
        .payload = (uint8_t *)msg,
        .len = strlen(msg),
    };
    httpd_ws_send_frame_async(server, fd, &frame);  // пристрій сам ініціює відправку
}
