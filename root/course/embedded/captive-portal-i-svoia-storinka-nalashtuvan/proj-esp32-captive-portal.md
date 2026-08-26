# ⚙️ Повний проект Captive Portal на ESP-IDF та C++

Цей проект демонструє автономний модуль первинного налаштування мікроконтролера, який поєднує бездротову точку доступу Wi-Fi SoftAP, перехоплювач DNS-запитів на базі сокетів Берклі (BSD Sockets UDP порт 53), легковагий вбудований HTTP-сервер (`esp_http_server`), розміщені у Flash-пам'яті стиснені ресурси інтерфейсу та транзакційне збереження конфігурації в Non-Volatile Storage (NVS).

### Архітектура системи та зв'язок компонентів

Проект організовано у вигляді модульної архітектури, що взаємодіє з системним мережевим стеком LWIP та планувальником FreeRTOS. Система виконує чотири послідовні інженерні задачі:

1. **Мережева ініціалізація точки доступу (`wifi_init_softap`)**: конфігурує віртуальний мережевий інтерфейс точки доступу з фіксованою адресою `192.168.4.1`, маскою `255.255.255.0` та запускає сервер DHCP з пулом адрес `192.168.4.2`–`192.168.4.10`.
2. **DNS Catch-all Server (`dns_server_task`)**: окреме завдання FreeRTOS, що слухає UDP-порт 53. Отримує будь-який запит типу A, інвертує прапорці заголовка на відповідь (Response, Authoritative, Recursion Available, No Error), встановлює `ANCOUNT = 1` та дописує 16-байтний запис ресурсу (Resource Record) з адресою `192.168.4.1`.
3. **HTTP Server (`http_server_init`)**: запускає пул обробників HTTP-запитів. Реєструє універсальний обробник перехоплення (Wildcard URI Handler), повертає статус `302 Found` для системних зондів Apple, Android та Windows, транслює з Flash-пам'яті стиснений GZIP веб-інтерфейс та приймає запити до REST API.
4. **Транзакційне збереження та таймер перезапуску**: валідує поля форми, записує облікові дані в NVS і відкладає виклик `esp_restart()` на 2 секунди за допомогою програмного таймера FreeRTOS, щоб стек TCP/IP встиг відправити `FIN/ACK` пакети й акуратно закрити з'єднання з клієнтом.

```
                    ┌──────────────────────────────────────────────────┐
                    │               ESP32 Wi-Fi SoftAP                 │
                    │               IP: 192.168.4.1                    │
                    └────────┬────────────────────────┬────────────────┘
                             │                        │
             UDP Port 53     ▼        TCP Port 80     ▼
     ┌─────────────────────────────┐   ┌─────────────────────────────┐
     │     DNS Catch-all Task      │   │     HTTP Web Server Task    │
     │  (Перехоплення імен у 53)   │   │ (Зонди 302, GZIP SPA, REST) │
     └──────────────┬──────────────┘   └──────────────┬──────────────┘
                    │                                 │
                    ▼                                 ▼
       Відповідь: 192.168.4.1             Запис у NVS + Рестарт
```

---

### 1. Реалізація DNS Catch-all сервера (UDP порт 53)

DNS-сервер не виділяє динамічну пам'ять у купі (Heap). Він використовує фіксований статичний буфер на 512 байтів на стеку FreeRTOS-завдання, модифікує отриманий вхідний пакет прямо за місцем і повертає його клієнту через виклик `sendto()`.

Такий підхід повністю захищає мікроконтролер від фрагментації оперативної пам'яті за умов інтенсивного бомбардування запитами від фонових служб смартфона.

Стек завдання DNS перехоплювача ізольовано від основного мережевого циклу, що гарантує миттєву відповідь на резолюцію імен навіть під час виконання важких операцій введення-виведення на веб-сервері.

:::tabs
```c
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define DNS_PORT 53
#define DNS_BUFFER_SIZE 512

static const char *TAG_DNS = "dns_server";

void dns_server_task(void *pvParameters) {
    uint8_t buffer[DNS_BUFFER_SIZE];
    struct sockaddr_in server_addr, client_addr;
    socklen_t client_len = sizeof(client_addr);

    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        ESP_LOGE(TAG_DNS, "Не вдалося створити UDP сокет");
        vTaskDelete(NULL);
        return;
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    server_addr.sin_port = htons(DNS_PORT);

    if (bind(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        ESP_LOGE(TAG_DNS, "Помилка прив'язки UDP порту 53");
        close(sock);
        vTaskDelete(NULL);
        return;
    }

    ESP_LOGI(TAG_DNS, "DNS Catch-all сервер успішно запущено на порту 53");

    while (1) {
        int len = recvfrom(sock, buffer, sizeof(buffer), 0,
                           (struct sockaddr *)&client_addr, &client_len);
        if (len < 12) {
            continue; // Пакет пошкоджений або коротший за заголовок DNS
        }

        // Прапорці відповіді: QR=1 (відповідь), AA=1 (авторитетна), RA=1, RCODE=0 (успіх)
        buffer[2] = 0x81;
        buffer[3] = 0x80;

        // Встановлюємо кількість відповідей ANCOUNT = 1
        buffer[6] = 0x00;
        buffer[7] = 0x01;

        // Обнуляємо лічильники NSCOUNT та ARCOUNT
        buffer[8] = 0x00; buffer[9] = 0x00;
        buffer[10] = 0x00; buffer[11] = 0x00;

        // Дописуємо блок Resource Record (Answer) наприкінці секції Question:
        // Вказівник на ім'я QNAME: 0xC00C (зміщення 12 на початок імені в запиті)
        buffer[len++] = 0xC0;
        buffer[len++] = 0x0C;

        // TYPE: 0x0001 (A - IPv4)
        buffer[len++] = 0x00;
        buffer[len++] = 0x01;

        // CLASS: 0x0001 (IN - Internet)
        buffer[len++] = 0x00;
        buffer[len++] = 0x01;

        // TTL: 10 секунд (0x0000000A)
        buffer[len++] = 0x00;
        buffer[len++] = 0x00;
        buffer[len++] = 0x00;
        buffer[len++] = 0x0A;

        // RDLENGTH: 4 байти для адреси IPv4
        buffer[len++] = 0x00;
        buffer[len++] = 0x04;

        // RDATA: 192.168.4.1 (0xC0, 0xA8, 0x04, 0x01)
        buffer[len++] = 192;
        buffer[len++] = 168;
        buffer[len++] = 4;
        buffer[len++] = 1;

        sendto(sock, buffer, len, 0, (struct sockaddr *)&client_addr, client_len);
    }
}
```
```cpp
#include <array>
#include <span>
#include <string_view>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace embedded::network {

class DnsCatchAllServer {
public:
    static constexpr uint16_t Port = 53;
    static constexpr size_t BufferCapacity = 512;
    static constexpr uint32_t TargetIp = 0xC0A80401; // 192.168.4.1 у network byte order

    void run() {
        int sockFd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (sockFd < 0) {
            ESP_LOGE(Tag.data(), "Помилка створення UDP сокета");
            return;
        }

        // RAII обгортка для безпечного закриття дескриптора сокета
        struct SocketGuard {
            int fd;
            ~SocketGuard() { if (fd >= 0) ::close(fd); }
        } guard{sockFd};

        sockaddr_in serverAddr{};
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_addr.s_addr = htonl(INADDR_ANY);
        serverAddr.sin_port = htons(Port);

        if (bind(sockFd, reinterpret_cast<sockaddr*>(&serverAddr), sizeof(serverAddr)) < 0) {
            ESP_LOGE(Tag.data(), "Помилка прив'язки UDP сокета до порту 53");
            return;
        }

        ESP_LOGI(Tag.data(), "C++ DNS Catch-all сервер активний на порту %u", Port);

        std::array<uint8_t, BufferCapacity> packetBuffer{};
        sockaddr_in clientAddr{};
        socklen_t clientLen = sizeof(clientAddr);

        while (true) {
            ssize_t receivedBytes = recvfrom(sockFd, packetBuffer.data(), packetBuffer.size(), 0,
                                             reinterpret_cast<sockaddr*>(&clientAddr), &clientLen);
            if (receivedBytes < 12) {
                continue;
            }

            auto bufferSpan = std::span<uint8_t>(packetBuffer.data(), packetBuffer.size());
            size_t replyLen = buildSpoofedResponse(bufferSpan, static_cast<size_t>(receivedBytes));

            sendto(sockFd, packetBuffer.data(), replyLen, 0,
                   reinterpret_cast<sockaddr*>(&clientAddr), clientLen);
        }
    }

private:
    static constexpr std::string_view Tag = "DnsCatchAll";

    static size_t buildSpoofedResponse(std::span<uint8_t> buf, size_t queryLen) noexcept {
        // Встановлюємо прапорці заголовка: Response, Authoritative, No Error
        buf[2] = 0x81;
        buf[3] = 0x80;
        buf[6] = 0x00; buf[7] = 0x01; // ANCOUNT = 1
        buf[8] = 0x00; buf[9] = 0x00; // NSCOUNT = 0
        buf[10] = 0x00; buf[11] = 0x00; // ARCOUNT = 0

        size_t offset = queryLen;
        // Дописування Resource Record (Answer)
        buf[offset++] = 0xC0; buf[offset++] = 0x0C; // Name Pointer to QNAME
        buf[offset++] = 0x00; buf[offset++] = 0x01; // Type A
        buf[offset++] = 0x00; buf[offset++] = 0x01; // Class IN
        buf[offset++] = 0x00; buf[offset++] = 0x00; 
        buf[offset++] = 0x00; buf[offset++] = 0x0A; // TTL = 10s
        buf[offset++] = 0x00; buf[offset++] = 0x04; // Data Length = 4
        buf[offset++] = 192;  buf[offset++] = 168;
        buf[offset++] = 4;    buf[offset++] = 1;    // IP: 192.168.4.1

        return offset;
    }
};

} // namespace embedded::network

extern "C" void dns_server_task_cpp(void *pvParameters) {
    embedded::network::DnsCatchAllServer server;
    server.run();
    vTaskDelete(nullptr);
}
```
:::

---

### 2. Вбудований асинхронний HTTP-сервер з обробкою 302 та REST API

HTTP-сервер реєструє маршрути точного співпадіння для майстра конфігурації та системних ендпоінтів, а для всіх невідомих зондових шляхів використовує шаблон підстановки `/*`, повертаючи заголовок `Location: http://192.168.4.1/setup`.

Вбудовані ресурси веб-інтерфейсу лінкуються безпосередньо у бінарний образ прошивки через директиву `EMBED_FILES` системи збірки CMake, що дозволяє віддавати їх клієнту за принципом Zero-Copy з адреси `index_html_gz_start` без виділення проміжних буферів RAM.

Під час сканування радіоефіру (`esp_wifi_scan_start`) модуль Wi-Fi тимчасово перемикається між каналами 1–13. Оскільки мікроконтролер працює у комбінованому режимі AP+STA, передача пакетів SoftAP на короткий час буферизується стеком, після чого веб-сервер повертає клієнту зібраний JSON-масив з показниками сили сигналу (RSSI) та типами шифрування кожної виявленої мережі.

:::tabs
```c
#include <stdlib.h>
#include <string.h>
#include "esp_http_server.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "cJSON.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"

static const char *TAG_HTTP = "http_server";
static TimerHandle_t s_reboot_timer = NULL;

extern const uint8_t index_html_gz_start[] asm("_binary_index_html_gz_start");
extern const uint8_t index_html_gz_end[]   asm("_binary_index_html_gz_end");

static void reboot_timer_callback(TimerHandle_t xTimer) {
    ESP_LOGI(TAG_HTTP, "Плановий перезапуск системи...");
    esp_restart();
}

static esp_err_t redirect_to_setup_handler(httpd_req_t *req) {
    httpd_resp_set_status(req, "302 Found");
    httpd_resp_set_hdr(req, "Location", "http://192.168.4.1/setup");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_send(req, NULL, 0);
    return ESP_OK;
}

static esp_err_t setup_page_handler(httpd_req_t *req) {
    size_t gz_len = index_html_gz_end - index_html_gz_start;
    httpd_resp_set_type(req, "text/html");
    httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_send(req, (const char *)index_html_gz_start, gz_len);
    return ESP_OK;
}

static esp_err_t api_scan_handler(httpd_req_t *req) {
    wifi_scan_config_t scan_config = {
        .ssid = 0, .bssid = 0, .channel = 0, .show_hidden = false
    };
    esp_wifi_scan_start(&scan_config, true);

    uint16_t ap_count = 0;
    esp_wifi_scan_get_ap_num(&ap_count);
    if (ap_count > 16) ap_count = 16;

    wifi_ap_record_t *ap_records = (wifi_ap_record_t *)malloc(sizeof(wifi_ap_record_t) * ap_count);
    if (!ap_records) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    esp_wifi_scan_get_ap_records(&ap_count, ap_records);

    cJSON *root = cJSON_CreateObject();
    cJSON *list = cJSON_CreateArray();

    for (int i = 0; i < ap_count; i++) {
        cJSON *item = cJSON_CreateObject();
        cJSON_AddStringToObject(item, "ssid", (const char *)ap_records[i].ssid);
        cJSON_AddNumberToObject(item, "rssi", ap_records[i].rssi);
        cJSON_AddNumberToObject(item, "channel", ap_records[i].primary);
        cJSON_AddItemToArray(list, item);
    }
    free(ap_records);

    cJSON_AddItemToObject(root, "networks", list);
    const char *json_str = cJSON_PrintUnformatted(root);

    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_sendstr(req, json_str);

    free((void *)json_str);
    cJSON_Delete(root);
    return ESP_OK;
}

static esp_err_t api_save_handler(httpd_req_t *req) {
    char buf[256];
    int ret = httpd_req_recv(req, buf, sizeof(buf) - 1);
    if (ret <= 0) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    buf[ret] = '\0';

    cJSON *json = cJSON_Parse(buf);
    if (!json) {
        httpd_resp_set_status(req, "400 Bad Request");
        httpd_resp_sendstr(req, "{\"status\":\"error\",\"message\":\"Invalid JSON\"}");
        return ESP_OK;
    }

    cJSON *j_ssid = cJSON_GetObjectItem(json, "ssid");
    cJSON *j_pass = cJSON_GetObjectItem(json, "password");

    if (!cJSON_IsString(j_ssid) || strlen(j_ssid->valuestring) == 0 || strlen(j_ssid->valuestring) > 32) {
        cJSON_Delete(json);
        httpd_resp_set_status(req, "400 Bad Request");
        httpd_resp_sendstr(req, "{\"status\":\"error\",\"message\":\"Invalid SSID length\"}");
        return ESP_OK;
    }

    nvs_handle_t nvs;
    if (nvs_open("wifi_cfg", NVS_READWRITE, &nvs) == ESP_OK) {
        nvs_set_str(nvs, "ssid", j_ssid->valuestring);
        if (cJSON_IsString(j_pass) && strlen(j_pass->valuestring) > 0) {
            nvs_set_str(nvs, "password", j_pass->valuestring);
        }
        nvs_set_u8(nvs, "configured", 1);
        nvs_commit(nvs);
        nvs_close(nvs);
    } else {
        cJSON_Delete(json);
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    cJSON_Delete(json);

    httpd_resp_set_type(req, "application/json");
    httpd_resp_sendstr(req, "{\"status\":\"ok\",\"message\":\"Saved. Rebooting in 2s...\"}");

    if (!s_reboot_timer) {
        s_reboot_timer = xTimerCreate("reboot_tmr", pdMS_TO_TICKS(2000), pdFALSE, NULL, reboot_timer_callback);
    }
    xTimerStart(s_reboot_timer, 0);

    return ESP_OK;
}

httpd_handle_t start_webserver(void) {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.wildcard_uri = true;
    config.max_uri_handlers = 8;
    httpd_handle_t server = NULL;

    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_uri_t uri_setup = { .uri = "/setup", .method = HTTP_GET, .handler = setup_page_handler };
        httpd_uri_t uri_root  = { .uri = "/",      .method = HTTP_GET, .handler = setup_page_handler };
        httpd_uri_t uri_scan  = { .uri = "/api/scan", .method = HTTP_GET, .handler = api_scan_handler };
        httpd_uri_t uri_save  = { .uri = "/api/save", .method = HTTP_POST, .handler = api_save_handler };
        httpd_uri_t uri_probe = { .uri = "/*",     .method = HTTP_GET, .handler = redirect_to_setup_handler };

        httpd_register_uri_handler(server, &uri_setup);
        httpd_register_uri_handler(server, &uri_root);
        httpd_register_uri_handler(server, &uri_scan);
        httpd_register_uri_handler(server, &uri_save);
        httpd_register_uri_handler(server, &uri_probe);
    }
    return server;
}
```
```cpp
#include <memory>
#include <span>
#include <string_view>
#include <vector>
#include <string>
#include "esp_http_server.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "cJSON.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"

extern const uint8_t index_html_gz_start[] asm("_binary_index_html_gz_start");
extern const uint8_t index_html_gz_end[]   asm("_binary_index_html_gz_end");

namespace embedded::web {

class NvsStorage {
public:
    static bool saveCredentials(std::string_view ssid, std::string_view pass) noexcept {
        nvs_handle_t handle{};
        if (nvs_open("wifi_cfg", NVS_READWRITE, &handle) != ESP_OK) {
            return false;
        }

        struct NvsGuard {
            nvs_handle_t h;
            ~NvsGuard() { nvs_close(h); }
        } guard{handle};

        std::string s(ssid);
        std::string p(pass);
        nvs_set_str(handle, "ssid", s.c_str());
        nvs_set_str(handle, "password", p.c_str());
        nvs_set_u8(handle, "configured", 1);
        return nvs_commit(handle) == ESP_OK;
    }
};

class PortalHttpServer {
public:
    static esp_err_t redirectToSetup(httpd_req_t *req) noexcept {
        httpd_resp_set_status(req, "302 Found");
        httpd_resp_set_hdr(req, "Location", "http://192.168.4.1/setup");
        httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
        httpd_resp_send(req, nullptr, 0);
        return ESP_OK;
    }

    static esp_err_t serveGzipSpa(httpd_req_t *req) noexcept {
        const size_t len = index_html_gz_end - index_html_gz_start;
        httpd_resp_set_type(req, "text/html");
        httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
        httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
        httpd_resp_send(req, reinterpret_cast<const char*>(index_html_gz_start), len);
        return ESP_OK;
    }

    static esp_err_t handleApiSave(httpd_req_t *req) noexcept {
        std::vector<char> buffer(256, 0);
        int bytesRead = httpd_req_recv(req, buffer.data(), buffer.size() - 1);
        if (bytesRead <= 0) {
            httpd_resp_send_500(req);
            return ESP_FAIL;
        }

        cJSON *root = cJSON_Parse(buffer.data());
        if (!root) {
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_sendstr(req, "{\"status\":\"error\",\"msg\":\"Bad JSON\"}");
            return ESP_OK;
        }

        struct JsonGuard {
            cJSON *obj;
            ~JsonGuard() { if (obj) cJSON_Delete(obj); }
        } guard{root};

        cJSON *jSsid = cJSON_GetObjectItem(root, "ssid");
        cJSON *jPass = cJSON_GetObjectItem(root, "password");

        if (!cJSON_IsString(jSsid) || strlen(j_ssid->valuestring) == 0 || strlen(j_ssid->valuestring) > 32) {
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_sendstr(req, "{\"status\":\"error\",\"msg\":\"Invalid SSID length\"}");
            return ESP_OK;
        }

        std::string_view ssidStr = jSsid->valuestring;
        std::string_view passStr = cJSON_IsString(jPass) ? jPass->valuestring : "";

        if (NvsStorage::saveCredentials(ssidStr, passStr)) {
            httpd_resp_set_type(req, "application/json");
            httpd_resp_sendstr(req, "{\"status\":\"ok\",\"msg\":\"Saved. Rebooting in 2s...\"}");

            static TimerHandle_t rebootTimer = xTimerCreate(
                "cpp_reboot", pdMS_TO_TICKS(2000), pdFALSE, nullptr,
                [](TimerHandle_t) { esp_restart(); });
            xTimerStart(rebootTimer, 0);
        } else {
            httpd_resp_send_500(req);
        }
        return ESP_OK;
    }
};

} // namespace embedded::web
```
:::

---

### 3. Ресурсний бюджет та налаштування FreeRTOS

Для забезпечення стабільної паралельної роботи бездротової точки доступу SoftAP, UDP сервера перехоплення DNS та асинхронного TCP сервера HTTP виділяються наступні системні ресурси:

1. **Стек завдань FreeRTOS:**
   - Завдання `dns_server_task`: фіксований розмір стеку `3072` байти. Цього достатньо для розміщення локального масиву на 512 байтів та внутрішніх структур сокетів LWIP без ризику переповнення стеку (Stack Overflow).
   - Завдання `httpd`: виділяється `4096` байтів стеку для обробки фрагментованих HTTP-заголовків, парсингу JSON та форматування відповідей.
2. **Ліміти підсистеми сокетів та дескрипторів:**
   - Максимальна кількість відкритих сокетів `max_open_sockets = 4` (1 сокет UDP для служби DNS + до 3 одночасних TCP-клієнтів).
   - Тайм-аут очікування даних `recv_wait_timeout = 5` секунд для запобігання утриманню з'єднань клієнтами, які несподівано відключилися від мережі або заблокували екран.
3. **Flash-пам'ять та зносостійкість:**
   - Секція констант `.rodata` для зберігання веб-інтерфейсу `index.html.gz`: ~`4` КБ.
   - Розділ `nvs`: виділяється щонайменше `0x4000` (16 КБ, що відповідає 4 секторам Flash по 4 КБ). Це забезпечує вирівнювання зносу комірок (Wear Leveling) при багаторазовому перезаписі конфігурації.

---

### 4. Пастки реалізації та крайові випадки

Практичне впровадження Captive Portal на мікроконтролерах вимагає врахування специфічних апаратних та протокольних нюансів:

1. **Уникнення витоку сокетів (Socket Leaks):** Якщо клієнтський смартфон раптово розриває зв'язок на фізичному рівні без відправки пакета `TCP FIN`, з'єднання на боці сервера залишається у стані `ESTABLISHED` до спрацьовування TCP Keep-Alive. Оскільки ліміт сокетів вбудованого сервера обмежений 4 дескрипторами, кілька таких відключень повністю паралізують веб-сервер. Встановлення малого таймауту `recv_wait_timeout = 5` та активація опції сокета `SO_RCVTIMEO` гарантує примусове закриття «мертвих» сесій.
2. **Асинхронне сканування без розриву SoftAP:** Сканування ефіру `esp_wifi_scan_start()` змушує радіотракт перемикатися між каналами. Щоб клієнт не втратив зв'язок із точкою доступу через пропуск кадрів маяків (Beacon frames), сканування запускається у пасивному або короткому активному режимі з періодом перебування на кожному каналі не більше 120 мілісекунд.
3. **Захист від апаратного скиду під час запису:** Будь-яке випадкове знеструмлення пристрою в момент виклику `nvs_commit()` може пошкодити блок даних, якщо не використовується транзакційна структура NVS. Використання штатного API `nvs_set_str()` з окремим ключем статусу `configured` гарантує, що частково записаний стан не буде прийнято за валідний при наступному старті.
