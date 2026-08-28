#include "esp_event.h"
#include "esp_wifi.h"

// Зібрати свіжий блоб із фактичних даних щойно вдалого підключення.
static void capture_and_save(const esp_netif_ip_info_t *ip_info)
{
    fastconn_t st = { 0 };
    st.magic   = FASTCONN_MAGIC;
    st.version = FASTCONN_VERSION;

    // Фактичний канал і BSSID точки, до якої під'єдналися.
    wifi_ap_record_t ap;
    if (esp_wifi_sta_get_ap_info(&ap) == ESP_OK) {
        st.channel = ap.primary;                 // реальний канал (1..13)
        memcpy(st.bssid, ap.bssid, sizeof(st.bssid));
    }

    // Адреса з події GOT_IP (уже в network order).
    st.ip      = ip_info->ip.addr;
    st.netmask = ip_info->netmask.addr;
    st.gw      = ip_info->gw.addr;

    st.fail_streak = 0;   // успіх обнуляє лічильник провалів

    if (fastconn_save(&st) == ESP_OK) {
        ESP_LOGI(TAG, "saved: ch=%u ip=" IPSTR,
                 st.channel, IP2STR(&ip_info->ip));
    }
}
