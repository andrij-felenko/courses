#include "portal/http_portal.hpp"

#include <array>
#include <chrono>
#include <span>
#include <string>
#include <string_view>

#include "esp_log.h"

#include "portal/credential_store.hpp"
#include "portal/deferred_reboot.hpp"
#include "portal/json_doc.hpp"
#include "portal/soft_ap.hpp"

/*
 * Сторінка потрапляє у прошивку стисненою, секцією .rodata. Віддаємо її
 * прямо з Flash за принципом zero-copy: жодного проміжного буфера в RAM,
 * а браузер розтискає потік сам, побачивши Content-Encoding: gzip.
 */
extern const std::uint8_t index_html_gz_start[] asm("_binary_index_html_gz_start");
extern const std::uint8_t index_html_gz_end[] asm("_binary_index_html_gz_end");

namespace portal::http {
namespace {

constexpr const char *kTag = "http";

/* Куди відправляємо клієнта з будь-якого перехопленого зонда. */
constexpr const char *kSetupUrl = "http://192.168.4.1/setup";

/* Тіло POST /api/save: два рядки й обгортка JSON — 256 байтів вистачає. */
constexpr std::size_t kSaveBodyMax = 256;

/* Скільки разів терпимо тайм-аут читання тіла, перш ніж кинути клієнта. */
constexpr int kRecvRetries = 3;

/* Пауза перед перезапуском: стек TCP/IP має встигнути віддати відповідь. */
constexpr auto kRebootDelay = std::chrono::milliseconds{2000};

[[nodiscard]] std::span<const std::uint8_t> embeddedPage() noexcept
{
    return {index_html_gz_start,
            static_cast<std::size_t>(index_html_gz_end - index_html_gz_start)};
}

/*
 * Сторінка майстра не має кешуватися: інакше після перезавантаження
 * пристрою браузер покаже її ж замість справжнього вмісту мережі.
 */
void setNoCache(httpd_req_t *request) noexcept
{
    httpd_resp_set_hdr(request, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_set_hdr(request, "Pragma", "no-cache");
}

esp_err_t sendJson(httpd_req_t *request, const char *status, const json::Doc &doc) noexcept
{
    const json::Text body = json::print(doc.get());
    if (!body) {
        return httpd_resp_send_500(request);
    }

    httpd_resp_set_status(request, status);
    httpd_resp_set_type(request, "application/json");
    setNoCache(request);
    return httpd_resp_sendstr(request, body.get());
}

esp_err_t sendError(httpd_req_t *request, const char *status, const char *message) noexcept
{
    json::Doc doc{cJSON_CreateObject()};
    if (!doc) {
        return httpd_resp_send_500(request);
    }
    cJSON_AddStringToObject(doc.get(), "status", "error");
    cJSON_AddStringToObject(doc.get(), "message", message);
    return sendJson(request, status, doc);
}

/* --- Перехоплення зондів ------------------------------------------------ */

/*
 * Сюди потрапляє все, що не збіглося з точними маршрутами: /generate_204
 * і /gen_204 від Android, /hotspot-detect.html від Apple, /ncsi.txt та
 * /connecttest.txt від Windows — і будь-яка адреса, набрана вручну.
 *
 * Відповідь 302 з полем Location і є сигналом «мережа за порталом»:
 * система бачить не той код, що чекала (204 або 200 з відомим тілом),
 * і сама відкриває вікно входу.
 */
esp_err_t handleCaptiveRedirect(httpd_req_t *request) noexcept
{
    ESP_LOGI(kTag, "Зонд %s → 302 на майстра", request->uri);

    httpd_resp_set_status(request, "302 Found");
    httpd_resp_set_hdr(request, "Location", kSetupUrl);
    setNoCache(request);
    return httpd_resp_send(request, nullptr, 0);
}

/* --- Сторінка майстра --------------------------------------------------- */

esp_err_t handleSetupPage(httpd_req_t *request) noexcept
{
    const std::span<const std::uint8_t> page = embeddedPage();

    httpd_resp_set_type(request, "text/html");
    httpd_resp_set_hdr(request, "Content-Encoding", "gzip");
    setNoCache(request);
    return httpd_resp_send(request, reinterpret_cast<const char *>(page.data()),
                           page.size());
}

/* --- GET /api/scan ------------------------------------------------------ */

esp_err_t handleScan(httpd_req_t *request) noexcept
{
    const auto networks = wifi::scan();
    if (!networks) {
        return sendError(request, "503 Service Unavailable", "scan failed");
    }

    json::Doc doc{cJSON_CreateObject()};
    if (!doc) {
        return httpd_resp_send_500(request);
    }

    cJSON *list = cJSON_AddArrayToObject(doc.get(), "networks");
    if (list == nullptr) {
        return httpd_resp_send_500(request);
    }

    for (const wifi::ScannedNetwork &network : *networks) {
        cJSON *item = cJSON_CreateObject();
        if (item == nullptr) {
            break;
        }
        const std::string authName{network.authName()};
        cJSON_AddStringToObject(item, "ssid", network.ssid.c_str());
        cJSON_AddNumberToObject(item, "rssi", network.rssi);
        cJSON_AddNumberToObject(item, "channel", network.channel);
        cJSON_AddStringToObject(item, "auth", authName.c_str());
        cJSON_AddItemToArray(list, item);
    }

    return sendJson(request, "200 OK", doc);
}

/* --- POST /api/save ----------------------------------------------------- */

[[nodiscard]] Result<std::string> receiveBody(httpd_req_t *request,
                                              std::size_t capacity) noexcept
{
    if (request->content_len == 0 || request->content_len > capacity) {
        return std::unexpected(ESP_ERR_INVALID_SIZE);
    }

    std::string body(request->content_len, '\0');
    std::size_t received = 0;
    int retries = kRecvRetries;

    while (received < body.size()) {
        const int chunk = httpd_req_recv(request, body.data() + received,
                                         body.size() - received);
        if (chunk == HTTPD_SOCK_ERR_TIMEOUT) {
            /* Клієнт замовк: даємо кілька спроб і звільняємо сокет. */
            if (--retries > 0) {
                continue;
            }
            return std::unexpected(ESP_ERR_TIMEOUT);
        }
        if (chunk <= 0) {
            return std::unexpected(ESP_FAIL);
        }
        received += static_cast<std::size_t>(chunk);
    }

    return body;
}

esp_err_t handleSave(httpd_req_t *request) noexcept
{
    const auto body = receiveBody(request, kSaveBodyMax);
    if (!body) {
        if (body.error() == ESP_ERR_INVALID_SIZE) {
            return sendError(request, "413 Payload Too Large", "body too large");
        }
        return sendError(request, "400 Bad Request", "incomplete body");
    }

    const json::Doc doc = json::parse(*body);
    if (!doc) {
        return sendError(request, "400 Bad Request", "malformed json");
    }

    if (!json::hasStringField(doc.get(), "ssid")) {
        return sendError(request, "400 Bad Request", "ssid required");
    }

    const std::string_view ssid = json::stringField(doc.get(), "ssid");
    if (ssid.empty() || ssid.size() > credentials::kSsidMax) {
        return sendError(request, "400 Bad Request", "ssid length 1..32");
    }

    const std::string_view password = json::stringField(doc.get(), "password");
    /* Порожній пароль означає відкриту мережу; WPA2 коротших за 8 не знає. */
    if (!password.empty() &&
        (password.size() < 8 || password.size() > credentials::kPasswordMax)) {
        return sendError(request, "400 Bad Request", "password length 8..63");
    }

    if (const auto saved = credentials::save(ssid, password); !saved) {
        return sendError(request, "500 Internal Server Error", "nvs write failed");
    }

    json::Doc reply{cJSON_CreateObject()};
    if (!reply) {
        return httpd_resp_send_500(request);
    }
    cJSON_AddStringToObject(reply.get(), "status", "ok");
    cJSON_AddStringToObject(reply.get(), "message", "saved");
    cJSON_AddNumberToObject(reply.get(), "reboot_ms",
                            static_cast<double>(kRebootDelay.count()));

    const esp_err_t sendResult = sendJson(request, "200 OK", reply);

    /*
     * Таймер заводимо після відправлення відповіді, але перезапуск однаково
     * відкладений: httpd_resp_sendstr лише передає дані стеку TCP/IP,
     * а той ще має дочекатися підтвердження від клієнта.
     */
    if (const auto scheduled = scheduleReboot(kRebootDelay); !scheduled) {
        ESP_LOGE(kTag, "Перезапуск не заплановано: %s",
                 esp_err_to_name(scheduled.error()));
    }

    return sendResult;
}

}  // namespace

Status Server::start() noexcept
{
    if (handle_ != nullptr) {
        return std::unexpected(ESP_ERR_INVALID_STATE);
    }

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 4096;        /* заголовки, парсинг JSON, форматування відповіді */
    config.max_uri_handlers = 8;
    config.max_open_sockets = 4;     /* UDP DNS живе поза сервером, тут — TCP-клієнти */
    config.lru_purge_enable = true;  /* новий клієнт витісняє найдавнішого, а не отримує відмову */

    /*
     * Телефон, що вимкнув екран або вийшов із зони, не встигає надіслати
     * FIN. З'єднання лишилося б у ESTABLISHED до спрацьовування keep-alive,
     * а чотирьох таких досить, щоб сервер перестав приймати нових.
     * Тайм-аути кладуть на сокет SO_RCVTIMEO/SO_SNDTIMEO і закривають
     * мертву сесію за п'ять секунд.
     */
    config.recv_wait_timeout = 5;
    config.send_wait_timeout = 5;

    /* Без цього збігача шаблон із зірочкою лишився б звичайним рядком. */
    config.uri_match_fn = httpd_uri_match_wildcard;

    httpd_handle_t handle = nullptr;
    if (const esp_err_t err = httpd_start(&handle, &config); err != ESP_OK) {
        ESP_LOGE(kTag, "httpd_start: %s", esp_err_to_name(err));
        return std::unexpected(err);
    }

    /*
     * Порядок реєстрації важить: збігач перебирає маршрути так, як їх
     * додали, тож універсальний перехоплювач має стояти останнім —
     * інакше він з'їв би й /setup, і REST.
     */
    constexpr std::array<httpd_uri_t, 5> routes{{
        {.uri = "/", .method = HTTP_GET, .handler = handleSetupPage, .user_ctx = nullptr},
        {.uri = "/setup", .method = HTTP_GET, .handler = handleSetupPage, .user_ctx = nullptr},
        {.uri = "/api/scan", .method = HTTP_GET, .handler = handleScan, .user_ctx = nullptr},
        {.uri = "/api/save", .method = HTTP_POST, .handler = handleSave, .user_ctx = nullptr},
        {.uri = "/*", .method = HTTP_GET, .handler = handleCaptiveRedirect, .user_ctx = nullptr},
    }};

    for (const httpd_uri_t &route : routes) {
        if (const esp_err_t err = httpd_register_uri_handler(handle, &route);
            err != ESP_OK) {
            ESP_LOGE(kTag, "Маршрут %s не зареєстровано: %s", route.uri,
                     esp_err_to_name(err));
            httpd_stop(handle);
            return std::unexpected(err);
        }
    }

    handle_ = handle;
    ESP_LOGI(kTag, "Веб-сервер порталу слухає порт %u",
             static_cast<unsigned>(config.server_port));
    return {};
}

void Server::stop() noexcept
{
    if (handle_ != nullptr) {
        httpd_stop(handle_);
        handle_ = nullptr;
    }
}

}  // namespace portal::http
