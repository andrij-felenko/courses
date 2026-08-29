#include <atomic>
#include <chrono>
#include <semaphore>
#include <string>

#include "esp_event.h"
#include "esp_log.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "nvs_flash.h"

#include "portal/credential_store.hpp"
#include "portal/dns_catch_all.hpp"
#include "portal/esp_result.hpp"
#include "portal/http_portal.hpp"
#include "portal/soft_ap.hpp"

namespace {

constexpr const char *kTag = "app";

/* Скільки разів пробуємо збережену мережу, перш ніж підняти портал. */
constexpr int kStationRetries = 5;

/* Скільки чекаємо на адресу від DHCP чужої мережі. */
constexpr auto kStationTimeout = std::chrono::seconds{20};

/* Прокидає очікувача, щойно доля підключення визначилася. */
std::binary_semaphore g_stationSettled{0};
std::atomic<bool> g_stationConnected{false};
std::atomic<int> g_stationRetries{0};

void onWifiEvent(void *, esp_event_base_t base, std::int32_t id, void *data) noexcept
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        const auto *event = static_cast<const wifi_event_sta_disconnected_t *>(data);

        if (g_stationRetries.fetch_add(1) + 1 <= kStationRetries) {
            ESP_LOGW(kTag, "Розрив зв'язку (причина %d), спроба %d із %d",
                     event->reason, g_stationRetries.load(), kStationRetries);
            esp_wifi_connect();
        } else {
            ESP_LOGE(kTag, "Збережена мережа недоступна, причина %d", event->reason);
            g_stationConnected.store(false);
            g_stationSettled.release();
        }
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        const auto *event = static_cast<const ip_event_got_ip_t *>(data);
        ESP_LOGI(kTag, "Отримано адресу " IPSTR, IP2STR(&event->ip_info.ip));
        g_stationRetries.store(0);
        g_stationConnected.store(true);
        g_stationSettled.release();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_AP_STACONNECTED) {
        const auto *event = static_cast<const wifi_event_ap_staconnected_t *>(data);
        ESP_LOGI(kTag, "До порталу під'єднався клієнт, aid=%d", event->aid);
    }
}

/*
 * Портал живе, доки живий пристрій, тож обидва сервери — статичні:
 * повернення з app_main не повинно їх зруйнувати.
 */
portal::Status startPortal() noexcept
{
    static portal::dns::CatchAllServer dnsServer{portal::wifi::accessPointIp()};
    static portal::http::Server httpServer;

    const std::string ssid = portal::wifi::accessPointName();

    return portal::wifi::startAccessPoint(ssid)
        .and_then([&] { return dnsServer.start(); })
        .and_then([&] { return httpServer.start(); })
        .and_then([&]() -> portal::Status {
            ESP_LOGI(kTag, "Портал налаштування працює: під'єднайтеся до \"%s\"",
                     ssid.c_str());
            return {};
        });
}

/*
 * Повертає true, коли збережена мережа справді піднялася. Помилка тут
 * не фатальна: пристрій просто вертається до порталу, бо пароль
 * домашнього роутера міг змінитися.
 */
bool trySavedNetwork() noexcept
{
    const auto credentials = portal::credentials::load();
    if (!credentials) {
        return false;
    }

    ESP_LOGI(kTag, "Пробуємо збережену мережу \"%s\"", credentials->ssid.c_str());

    if (const auto started =
            portal::wifi::connectStation(credentials->ssid, credentials->password);
        !started) {
        return false;
    }

    if (!g_stationSettled.try_acquire_for(kStationTimeout)) {
        /* Ні адреси, ні остаточної відмови — далі чекати немає сенсу. */
        esp_wifi_disconnect();
        return false;
    }

    return g_stationConnected.load();
}

portal::Status initSystem() noexcept
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        /* Розділ лишився від старішої прошивки або переповнений — чистимо. */
        if (const auto erased = portal::check(nvs_flash_erase()); !erased) {
            return erased;
        }
        err = nvs_flash_init();
    }

    return portal::check(err)
        .and_then([] { return portal::check(esp_netif_init()); })
        .and_then([] { return portal::check(esp_event_loop_create_default()); })
        .and_then([] {
            return portal::check(esp_event_handler_instance_register(
                WIFI_EVENT, ESP_EVENT_ANY_ID, &onWifiEvent, nullptr, nullptr));
        })
        .and_then([] {
            return portal::check(esp_event_handler_instance_register(
                IP_EVENT, IP_EVENT_STA_GOT_IP, &onWifiEvent, nullptr, nullptr));
        })
        .and_then([] { return portal::wifi::initStack(); });
}

}  // namespace

extern "C" void app_main()
{
    if (const auto ready = initSystem(); !ready) {
        ESP_LOGE(kTag, "Ініціалізація не вдалася: %s", esp_err_to_name(ready.error()));
        return;
    }

    if (portal::credentials::isConfigured() && trySavedNetwork()) {
        ESP_LOGI(kTag, "Робочий режим: портал не потрібен");
        return;
    }

    /*
     * Або конфігурації немає взагалі (пристрій щойно з конвеєра), або
     * збережена мережа не піднялася. Обидва випадки ведуть в одне місце —
     * до сторінки налаштувань.
     */
    if (const auto started = startPortal(); !started) {
        ESP_LOGE(kTag, "Портал не піднявся: %s", esp_err_to_name(started.error()));
    }
}
