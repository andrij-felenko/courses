#include "lwip/netif.h"
#include "lwip/ip_addr.h"
#include <stdio.h>

// Функція інспектування стану мережевого адаптера netif у C
void inspect_netif_station(void) {
    // Отримання замовчуваного мережевого інтерфейсу (Station)
    struct netif *netif = netif_default;

    if (netif == NULL) {
        printf("Мережевий адаптер netif не ініціалізовано!\n");
        return;
    }

    // Перевірка прапорів готовності інтерфейсу
    if (netif_is_up(netif) && netif_is_link_up(netif)) {
        printf("Інтерфейс %c%c%u активний\n", netif->name[0], netif->name[1], netif->num);
        printf("IP-адреса : %s\n", ipaddr_ntoa(&netif->ip_addr));
        printf("Маска     : %s\n", ipaddr_ntoa(&netif->netmask));
        printf("Шлюз      : %s\n", ipaddr_ntoa(&netif->gw));
        printf("MAC-адреса: %02x:%02x:%02x:%02x:%02x:%02x\n",
               netif->hwaddr[0], netif->hwaddr[1], netif->hwaddr[2],
               netif->hwaddr[3], netif->hwaddr[4], netif->hwaddr[5]);
    } else {
        printf("Мережевий адаптер netif перебуває у стані DOWN\n");
    }
}
