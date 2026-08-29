#include "portal/soft_ap.hpp"

#include <algorithm>
#include <array>
#include <cstdio>
#include <cstring>

#include "dhcpserver/dhcpserver.h"
#include "esp_log.h"
#include "esp_netif.h"

namespace portal::wifi {
namespace {

constexpr const char *kTag = "wifi";

esp_netif_t *g_apNetif = nullptr;
esp_netif_t *g_staNetif = nullptr;

/*
 * Копіює рядок у масив фіксованої довжини драйвера. Нуль дописуємо лише
 * тоді, коли для нього лишилося місце: SSID рівно на 32 октети — законний,
 * і його справжню довжину драйвер бере з окремого поля ssid_len.
 */
template <std::size_t N>
std::size_t assignField(std::uint8_t (&field)[N], std::string_view value) noexcept
{
    const std::size_t length = std::min(value.size(), N);
    std::memcpy(field, value.data(), length);
    if (length < N) {
        field[length] = '\0';
    }
    return length;
}

Status configureApAddressing() noexcept
{
    /* Перелаштовувати адресацію можна лише при зупиненому сервері DHCP. */
    const esp_err_t stopErr = esp_netif_dhcps_stop(g_apNetif);
    if (stopErr != ESP_OK && stopErr != ESP_ERR_ESP_NETIF_DHCP_ALREADY_STOPPED) {
        return std::unexpected(stopErr);
    }

    esp_netif_ip_info_t ipInfo{};
    ipInfo.ip.addr = esp_ip4addr_aton(kApAddress);
    ipInfo.gw.addr = esp_ip4addr_aton(kApAddress);
    ipInfo.netmask.addr = esp_ip4addr_aton(kApNetmask);
    if (auto status = check(esp_netif_set_ip_info(g_apNetif, &ipInfo)); !status) {
        return status;
    }

    dhcps_lease_t pool{
        .enable = true,
        .start_ip = {.addr = esp_ip4addr_aton(kDhcpPoolStart)},
        .end_ip = {.addr = esp_ip4addr_aton(kDhcpPoolEnd)},
    };
    if (auto status = check(esp_netif_dhcps_option(
            g_apNetif, ESP_NETIF_OP_SET, ESP_NETIF_REQUESTED_IP_ADDRESS,
            &pool, sizeof(pool)));
        !status) {
        return status;
    }

    /*
     * Ключовий для порталу крок: сервер DHCP має віддавати клієнтові
     * як DNS-сервер саме нас. Без цієї опції телефон піде питати імена
     * у сервера, який запам'ятав раніше, і перехоплювач на порту 53
     * не побачить жодного запиту.
     */
    dhcps_offer_t dnsOffer = OFFER_DNS;
    if (auto status = check(esp_netif_dhcps_option(
            g_apNetif, ESP_NETIF_OP_SET, ESP_NETIF_DOMAIN_NAME_SERVER,
            &dnsOffer, sizeof(dnsOffer)));
        !status) {
        return status;
    }

    esp_netif_dns_info_t dnsInfo{};
    dnsInfo.ip.type = ESP_IPADDR_TYPE_V4;
    dnsInfo.ip.u_addr.ip4.addr = esp_ip4addr_aton(kApAddress);
    if (auto status = check(esp_netif_set_dns_info(g_apNetif, ESP_NETIF_DNS_MAIN,
                                                   &dnsInfo));
        !status) {
        return status;
    }

    return check(esp_netif_dhcps_start(g_apNetif));
}

}  // namespace

std::string_view ScannedNetwork::authName() const noexcept
{
    switch (auth) {
        case WIFI_AUTH_OPEN:            return "open";
        case WIFI_AUTH_WEP:             return "wep";
        case WIFI_AUTH_WPA_PSK:         return "wpa";
        case WIFI_AUTH_WPA2_PSK:        return "wpa2";
        case WIFI_AUTH_WPA_WPA2_PSK:    return "wpa/wpa2";
        case WIFI_AUTH_WPA2_ENTERPRISE: return "wpa2-enterprise";
        case WIFI_AUTH_WPA3_PSK:        return "wpa3";
        case WIFI_AUTH_WPA2_WPA3_PSK:   return "wpa2/wpa3";
        case WIFI_AUTH_WAPI_PSK:        return "wapi";
        default:                        return "unknown";
    }
}

Status initStack() noexcept
{
    if (g_apNetif != nullptr) {
        return {};
    }

    g_apNetif = esp_netif_create_default_wifi_ap();
    g_staNetif = esp_netif_create_default_wifi_sta();
    if (g_apNetif == nullptr || g_staNetif == nullptr) {
        return std::unexpected(ESP_ERR_NO_MEM);
    }

    wifi_init_config_t initConfig = WIFI_INIT_CONFIG_DEFAULT();
    if (auto status = check(esp_wifi_init(&initConfig)); !status) {
        return status;
    }

    /*
     * Драйвер за замовчуванням дублює свою конфігурацію в NVS на кожній
     * зміні режиму. Власні параметри ми зберігаємо самі, а зайві цикли
     * стирання витрачають ресурс Flash.
     */
    if (auto status = check(esp_wifi_set_storage(WIFI_STORAGE_RAM)); !status) {
        return status;
    }

    return check(esp_wifi_set_mode(WIFI_MODE_APSTA));
}

Status startAccessPoint(std::string_view ssid, std::string_view password) noexcept
{
    if (ssid.empty()) {
        return std::unexpected(ESP_ERR_INVALID_ARG);
    }

    if (auto status = configureApAddressing(); !status) {
        ESP_LOGE(kTag, "Адресацію точки доступу не налаштовано: %s",
                 esp_err_to_name(status.error()));
        return status;
    }

    wifi_config_t config{};
    config.ap.ssid_len = static_cast<std::uint8_t>(assignField(config.ap.ssid, ssid));
    config.ap.channel = 1;
    config.ap.max_connection = 4;
    config.ap.beacon_interval = 100;

    if (!password.empty()) {
        assignField(config.ap.password, password);
        config.ap.authmode = WIFI_AUTH_WPA2_PSK;
    } else {
        /* Портал первинного налаштування свідомо відкритий: пароль до нього
         * довелося б десь надрукувати, а це вже не zero-config. */
        config.ap.authmode = WIFI_AUTH_OPEN;
    }

    if (auto status = check(esp_wifi_set_config(WIFI_IF_AP, &config)); !status) {
        return status;
    }
    if (auto status = check(esp_wifi_start()); !status) {
        return status;
    }

    ESP_LOGI(kTag, "Точку доступу \"%.*s\" піднято на %s",
             static_cast<int>(ssid.size()), ssid.data(), kApAddress);
    return {};
}

Status connectStation(std::string_view ssid, std::string_view password) noexcept
{
    if (ssid.empty()) {
        return std::unexpected(ESP_ERR_INVALID_ARG);
    }

    wifi_config_t config{};
    assignField(config.sta.ssid, ssid);
    assignField(config.sta.password, password);
    config.sta.threshold.authmode =
        password.empty() ? WIFI_AUTH_OPEN : WIFI_AUTH_WPA_PSK;

    if (auto status = check(esp_wifi_set_config(WIFI_IF_STA, &config)); !status) {
        return status;
    }

    const esp_err_t startErr = esp_wifi_start();
    if (startErr != ESP_OK && startErr != ESP_ERR_WIFI_NOT_STOPPED) {
        return std::unexpected(startErr);
    }

    return check(esp_wifi_connect());
}

Result<std::vector<ScannedNetwork>> scan(std::size_t limit) noexcept
{
    /*
     * Сканування змушує радіотракт залишити канал точки доступу й обійти
     * канали 1–13. Поки він мандрує, кадри-маяки нашої мережі не виходять
     * в ефір, і клієнт може вирішити, що точка зникла. Тому час перебування
     * на каналі обмежено 120 мс: за таку паузу телефон зв'язок не рве.
     */
    wifi_scan_config_t scanConfig{};
    scanConfig.show_hidden = false;
    scanConfig.scan_type = WIFI_SCAN_TYPE_ACTIVE;
    scanConfig.scan_time.active.min = 60;
    scanConfig.scan_time.active.max = 120;

    if (const esp_err_t err = esp_wifi_scan_start(&scanConfig, true); err != ESP_OK) {
        ESP_LOGE(kTag, "Сканування не стартувало: %s", esp_err_to_name(err));
        return std::unexpected(err);
    }

    std::uint16_t found = 0;
    if (const esp_err_t err = esp_wifi_scan_get_ap_num(&found); err != ESP_OK) {
        esp_wifi_clear_ap_list();
        return std::unexpected(err);
    }

    const auto wanted = static_cast<std::uint16_t>(
        std::min<std::size_t>(found, limit));
    if (wanted == 0) {
        /* Драйвер тримає список у купі, доки його не забрали або не скинули. */
        esp_wifi_clear_ap_list();
        return std::vector<ScannedNetwork>{};
    }

    std::vector<wifi_ap_record_t> records(wanted);
    std::uint16_t count = wanted;
    if (const esp_err_t err = esp_wifi_scan_get_ap_records(&count, records.data());
        err != ESP_OK) {
        esp_wifi_clear_ap_list();
        return std::unexpected(err);
    }
    records.resize(count);

    std::vector<ScannedNetwork> networks;
    networks.reserve(records.size());
    for (const wifi_ap_record_t &record : records) {
        networks.push_back(ScannedNetwork{
            .ssid = std::string{reinterpret_cast<const char *>(record.ssid)},
            .rssi = record.rssi,
            .channel = record.primary,
            .auth = record.authmode,
        });
    }

    ESP_LOGI(kTag, "Знайдено мереж: %u (віддаємо %u)",
             static_cast<unsigned>(found), static_cast<unsigned>(networks.size()));
    return networks;
}

std::string accessPointName() noexcept
{
    std::array<std::uint8_t, 6> mac{};
    esp_wifi_get_mac(WIFI_IF_AP, mac.data());

    std::array<char, 32> name{};
    std::snprintf(name.data(), name.size(), "ESP32-Setup-%02X%02X", mac[4], mac[5]);
    return std::string{name.data()};
}

std::uint32_t accessPointIp() noexcept
{
    return esp_ip4addr_aton(kApAddress);
}

}  // namespace portal::wifi
