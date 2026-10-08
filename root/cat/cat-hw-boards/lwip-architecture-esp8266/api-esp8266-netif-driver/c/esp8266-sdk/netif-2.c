#include "lwip/netif.h"
#include "lwip/dhcp.h"

// Зворотний виклик зміни статусу IP-адресації
static void netif_status_callback(struct netif *netif) {
    if (netif_is_up(netif) && !ip4_addr_isany_val(*netif_ip4_addr(netif))) {
        // Отримано дійсну IP-адресу (наприклад, через DHCP)
        printf("IP отримано: %s\n", ip4addr_ntoa(netif_ip4_addr(netif)));
    }
}

// Зворотний виклик зміни фізичного линка Wi-Fi
static void netif_link_callback(struct netif *netif) {
    if (netif_is_link_up(netif)) {
        printf("Wi-Fi фізично підключено. Запуск DHCP...\n");
        dhcp_start(netif);
    } else {
        printf("Wi-Fi зв'язок втрачено! Зупинка DHCP...\n");
        dhcp_stop(netif);
    }
}

// Налаштування зворотних викликів для адаптера
void setup_netif_event_handlers(struct netif *netif) {
    netif_set_status_callback(netif, netif_status_callback);
    netif_set_link_callback(netif, netif_link_callback);
}

// Обробник подій Wi-Fi драйвера ESP8266
void on_wifi_event(int event_id, struct netif *netif) {
    switch (event_id) {
        case WIFI_EVENT_STA_CONNECTED:
            netif_set_link_up(netif);
            break;
        case WIFI_EVENT_STA_DISCONNECTED:
            netif_set_link_down(netif);
            break;
        default:
            break;
    }
}
