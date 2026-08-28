#include "esp_netif.h"

// Прошити збережену адресу статично: DHCP вимикаємо, фази немає зовсім.
static void apply_static_ip(esp_netif_t *netif, const fastconn_t *st)
{
    // 1. Зупинити DHCP-клієнта. ALREADY_STOPPED тут — не помилка.
    esp_err_t err = esp_netif_dhcpc_stop(netif);
    if (err != ESP_OK && err != ESP_ERR_ESP_NETIF_DHCP_ALREADY_STOPPED) {
        ESP_LOGW(TAG, "dhcpc_stop: %s", esp_err_to_name(err));
        return;
    }

    // 2. Прописати IP/маску/шлюз з блоба (вони вже в network order).
    esp_netif_ip_info_t ip = { 0 };
    ip.ip.addr      = st->ip;
    ip.netmask.addr = st->netmask;
    ip.gw.addr      = st->gw;
    ESP_ERROR_CHECK(esp_netif_set_ip_info(netif, &ip));
}
