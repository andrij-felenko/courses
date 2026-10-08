#include "lwip/netif.h"
#include "lwip/ip_addr.h"
#include "netif/etharp.h"

// Приватна структура контексту драйвера Wi-Fi
typedef struct {
    uint8_t mac_addr[6];
    bool is_station;
} esp8266_wifi_driver_t;

static esp8266_wifi_driver_t sta_driver_ctx;
static struct netif sta_netif;

// Прототип низькорівневої функції відправлення
static err_t low_level_output(struct netif *netif, struct pbuf *p);

// Функція ініціалізації низькорівневого адаптера
static err_t esp8266_wifi_if_init(struct netif *netif) {
    esp8266_wifi_driver_t *drv = (esp8266_wifi_driver_t *)netif->state;
    
    netif->name[0] = 's';
    netif->name[1] = 't';
    netif->output = etharp_output;
    netif->linkoutput = low_level_output;
    netif->mtu = 1500;
    netif->flags = NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP | NETIF_FLAG_IGMP;
    
    netif->hwaddr_len = 6;
    memcpy(netif->hwaddr, drv->mac_addr, 6);
    
    return ERR_OK;
}

// Процедура реєстрації мережевого інтерфейсу
void esp8266_network_init(void) {
    ip4_addr_t ipaddr, netmask, gw;
    
    // Ініціалізація початкових значень IP (0.0.0.0 для очікування DHCP)
    IP4_ADDR(&ipaddr, 0, 0, 0, 0);
    IP4_ADDR(&netmask, 0, 0, 0, 0);
    IP4_ADDR(&gw, 0, 0, 0, 0);

    sta_driver_ctx.mac_addr[0] = 0x5C;
    sta_driver_ctx.mac_addr[1] = 0xCF;
    sta_driver_ctx.mac_addr[2] = 0x7F;
    sta_driver_ctx.mac_addr[3] = 0x12;
    sta_driver_ctx.mac_addr[4] = 0x34;
    sta_driver_ctx.mac_addr[5] = 0x56;

    // Реєстрація інтерфейсу в стеку lwIP
    netif_add(&sta_netif, &ipaddr, &netmask, &gw, 
              &sta_driver_ctx, esp8266_wifi_if_init, ethernet_input);

    // Встановлення інтерфейсу за замовчуванням та його активація
    netif_set_default(&sta_netif);
    netif_set_up(&sta_netif);
}
