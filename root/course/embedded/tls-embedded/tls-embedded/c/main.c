#include "esp_tls.h"

// кореневий сертифікат CA — зашитий у прошивку (масив байтів у Flash).
// без нього перевірити сервер нічим — і весь захист від самозванця зникає.
extern const uint8_t ca_pem_start[] asm("_binary_ca_pem_start");
extern const uint8_t ca_pem_end[]   asm("_binary_ca_pem_end");

void send_reading(float temp_c) {
    esp_tls_cfg_t cfg = {
        .cacert_buf   = ca_pem_start,               // ← ось той корінь довіри
        .cacert_bytes = ca_pem_end - ca_pem_start,
        // за замовчуванням бібліотека ПЕРЕВІРЯЄ сертифікат сервера цим коренем.
        // .skip_common_name чи вимикання перевірки тут НЕ чіпаємо — це діра.
    };

    // одним викликом: TCP-з'єднання + рукостискання TLS + перевірка сертифіката
    esp_tls_t *tls = esp_tls_init();
    if (esp_tls_conn_http_new_sync("https://api.example.com", &cfg, tls) != 1) {
        esp_tls_conn_destroy(tls);
        return;                                     // не зійшлось — назовні НІЧОГО не пішло
    }

    char body[64];
    int n = snprintf(body, sizeof body, "{\"t\":%.1f}", temp_c);

    // з цієї миті write/read шифрують і перевіряють кожен байт автоматично
    esp_tls_conn_write(tls, body, n);

    esp_tls_conn_destroy(tls);                      // закрити з'єднання й звільнити пам'ять
}
