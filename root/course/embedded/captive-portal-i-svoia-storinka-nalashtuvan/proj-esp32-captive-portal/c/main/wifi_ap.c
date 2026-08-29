#include "wifi_ap.h"

#include <string.h>

#include "dhcpserver/dhcpserver.h"
#include "esp_log.h"
#include "esp_netif.h"

static const char *TAG = "wifi";

static esp_netif_t *s_ap_netif = NULL;
static esp_netif_t *s_sta_netif = NULL;

esp_err_t wifi_stack_init(void)
{
    if (s_ap_netif != NULL) {
        return ESP_OK;
    }

    s_ap_netif = esp_netif_create_default_wifi_ap();
    s_sta_netif = esp_netif_create_default_wifi_sta();
    if (s_ap_netif == NULL || s_sta_netif == NULL) {
        return ESP_ERR_NO_MEM;
    }

    wifi_init_config_t init_cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_err_t err = esp_wifi_init(&init_cfg);
    if (err != ESP_OK) {
        return err;
    }

    /*
     * Драйвер за замовчуванням дублює свою конфігурацію в NVS на кожній
     * зміні режиму. Нам це не потрібно — власні параметри ми зберігаємо
     * самі, — а зайві цикли стирання витрачають ресурс Flash.
     */
    err = esp_wifi_set_storage(WIFI_STORAGE_RAM);
    if (err != ESP_OK) {
        return err;
    }

    return esp_wifi_set_mode(WIFI_MODE_APSTA);
}

static esp_err_t configure_ap_addressing(void)
{
    /* Перелаштовувати адресацію можна лише при зупиненому сервері DHCP. */
    esp_err_t err = esp_netif_dhcps_stop(s_ap_netif);
    if (err != ESP_OK && err != ESP_ERR_ESP_NETIF_DHCP_ALREADY_STOPPED) {
        return err;
    }

    esp_netif_ip_info_t ip_info = {0};
    ip_info.ip.addr = esp_ip4addr_aton(WIFI_AP_IP_ADDR);
    ip_info.gw.addr = esp_ip4addr_aton(WIFI_AP_IP_ADDR);
    ip_info.netmask.addr = esp_ip4addr_aton(WIFI_AP_NETMASK);
    err = esp_netif_set_ip_info(s_ap_netif, &ip_info);
    if (err != ESP_OK) {
        return err;
    }

    dhcps_lease_t pool = {
        .enable = true,
        .start_ip.addr = esp_ip4addr_aton(WIFI_AP_DHCP_POOL_START),
        .end_ip.addr = esp_ip4addr_aton(WIFI_AP_DHCP_POOL_END),
    };
    err = esp_netif_dhcps_option(s_ap_netif, ESP_NETIF_OP_SET,
                                 ESP_NETIF_REQUESTED_IP_ADDRESS,
                                 &pool, sizeof(pool));
    if (err != ESP_OK) {
        return err;
    }

    /*
     * Ключовий для порталу крок: сервер DHCP має віддавати клієнтові
     * як DNS-сервер саме нас. Без цієї опції телефон піде питати імена
     * у сервера, який запам'ятав раніше, і перехоплювач на порту 53
     * не побачить жодного запиту.
     */
    dhcps_offer_t dns_offer = OFFER_DNS;
    err = esp_netif_dhcps_option(s_ap_netif, ESP_NETIF_OP_SET,
                                 ESP_NETIF_DOMAIN_NAME_SERVER,
                                 &dns_offer, sizeof(dns_offer));
    if (err != ESP_OK) {
        return err;
    }

    esp_netif_dns_info_t dns_info = {0};
    dns_info.ip.type = ESP_IPADDR_TYPE_V4;
    dns_info.ip.u_addr.ip4.addr = esp_ip4addr_aton(WIFI_AP_IP_ADDR);
    err = esp_netif_set_dns_info(s_ap_netif, ESP_NETIF_DNS_MAIN, &dns_info);
    if (err != ESP_OK) {
        return err;
    }

    return esp_netif_dhcps_start(s_ap_netif);
}

esp_err_t wifi_ap_start(const char *ssid, const char *password)
{
    if (ssid == NULL || ssid[0] == '\0') {
        return ESP_ERR_INVALID_ARG;
    }

    esp_err_t err = configure_ap_addressing();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Адресацію точки доступу не налаштовано: %s", esp_err_to_name(err));
        return err;
    }

    wifi_config_t cfg = {0};

    /* Поле драйвера — рівно 32 октети без завершального нуля; справжню
     * довжину він бере з ssid_len, тож довше ім'я просто обрізаємо. */
    size_t ssid_len = strlen(ssid);
    if (ssid_len > sizeof(cfg.ap.ssid)) {
        ssid_len = sizeof(cfg.ap.ssid);
    }
    memcpy(cfg.ap.ssid, ssid, ssid_len);
    cfg.ap.ssid_len = (uint8_t)ssid_len;
    cfg.ap.channel = 1;
    cfg.ap.max_connection = 4;
    cfg.ap.beacon_interval = 100;

    if (password != NULL && password[0] != '\0') {
        strlcpy((char *)cfg.ap.password, password, sizeof(cfg.ap.password));
        cfg.ap.authmode = WIFI_AUTH_WPA2_PSK;
    } else {
        /* Портал первинного налаштування свідомо відкритий: пароль
         * до нього довелося б десь надрукувати, а це вже не zero-config. */
        cfg.ap.authmode = WIFI_AUTH_OPEN;
    }

    err = esp_wifi_set_config(WIFI_IF_AP, &cfg);
    if (err != ESP_OK) {
        return err;
    }

    err = esp_wifi_start();
    if (err != ESP_OK) {
        return err;
    }

    ESP_LOGI(TAG, "Точку доступу \"%s\" піднято на %s", ssid, WIFI_AP_IP_ADDR);
    return ESP_OK;
}

esp_err_t wifi_sta_connect(const char *ssid, const char *password)
{
    if (ssid == NULL || ssid[0] == '\0') {
        return ESP_ERR_INVALID_ARG;
    }

    wifi_config_t cfg = {0};
    strlcpy((char *)cfg.sta.ssid, ssid, sizeof(cfg.sta.ssid));
    if (password != NULL) {
        strlcpy((char *)cfg.sta.password, password, sizeof(cfg.sta.password));
    }
    cfg.sta.threshold.authmode = (password != NULL && password[0] != '\0')
                                     ? WIFI_AUTH_WPA_PSK
                                     : WIFI_AUTH_OPEN;

    esp_err_t err = esp_wifi_set_config(WIFI_IF_STA, &cfg);
    if (err != ESP_OK) {
        return err;
    }

    err = esp_wifi_start();
    if (err != ESP_OK && err != ESP_ERR_WIFI_NOT_STOPPED) {
        return err;
    }

    return esp_wifi_connect();
}

esp_err_t wifi_ap_scan(wifi_ap_record_t *out, uint16_t *count)
{
    if (out == NULL || count == NULL || *count == 0) {
        return ESP_ERR_INVALID_ARG;
    }

    /*
     * Сканування змушує радіотракт залишити канал точки доступу й обійти
     * канали 1–13. Поки він мандрує, кадри-маяки нашої ж мережі не виходять
     * в ефір, і клієнт може вирішити, що точка зникла. Тому час перебування
     * на каналі обмежено 120 мс: за стандартом клієнт чекає маяка кілька
     * інтервалів по 100 мс і за таку паузу зв'язок не рве.
     */
    wifi_scan_config_t scan_cfg = {
        .ssid = NULL,
        .bssid = NULL,
        .channel = 0,
        .show_hidden = false,
        .scan_type = WIFI_SCAN_TYPE_ACTIVE,
        .scan_time.active.min = 60,
        .scan_time.active.max = 120,
    };

    esp_err_t err = esp_wifi_scan_start(&scan_cfg, true);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Сканування не стартувало: %s", esp_err_to_name(err));
        return err;
    }

    uint16_t found = 0;
    err = esp_wifi_scan_get_ap_num(&found);
    if (err != ESP_OK) {
        esp_wifi_clear_ap_list();
        return err;
    }

    uint16_t capacity = *count;
    if (found < capacity) {
        capacity = found;
    }

    if (capacity == 0) {
        /* Драйвер тримає список у купі, доки його не забрали або не скинули. */
        esp_wifi_clear_ap_list();
        *count = 0;
        return ESP_OK;
    }

    err = esp_wifi_scan_get_ap_records(&capacity, out);
    if (err != ESP_OK) {
        esp_wifi_clear_ap_list();
        return err;
    }

    *count = capacity;
    ESP_LOGI(TAG, "Знайдено мереж: %u (віддаємо %u)", (unsigned)found, (unsigned)capacity);
    return ESP_OK;
}

const char *wifi_auth_name(wifi_auth_mode_t mode)
{
    switch (mode) {
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
