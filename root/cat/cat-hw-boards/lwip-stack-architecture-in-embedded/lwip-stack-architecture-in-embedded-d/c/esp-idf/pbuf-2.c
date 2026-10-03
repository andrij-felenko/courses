#include "lwip/netif.h"
#include "lwip/pbuf.h"
#include "netif/etharp.h"
#include "lwip/tcpip.h"

// Приватний контекст драйвера Ethernet
typedef struct {
    uint8_t mac_addr[6];
    void *dma_tx_descriptors;
    void *dma_rx_descriptors;
} custom_eth_driver_t;

// Передача пакета у фізичний канал
static err_t low_level_output(struct netif *netif, struct pbuf *p) {
    custom_eth_driver_t *drv = (custom_eth_driver_t *)netif->state;
    struct pbuf *q;

    // Ітерація по ланцюжку pbuf та копіювання у DMA буфер
    for (q = p; q != NULL; q = q->next) {
        // Копіювання q->payload довжиною q->len в апаратний TX дескриптор DMA
    }
    
    // Запуск апаратної передачі кадру
    
    LINK_STATS_INC(link.xmit);
    return ERR_OK;
}

// Прийом пакета з апаратного кільця DMA
static struct pbuf* low_level_input(struct netif *netif, uint8_t *rx_frame, uint16_t len) {
    struct pbuf *p = pbuf_alloc(PBUF_RAW, len, PBUF_POOL);
    if (p != NULL) {
        struct pbuf *q;
        uint16_t offset = 0;
        for (q = p; q != NULL; q = q->next) {
            memcpy(q->payload, rx_frame + offset, q->len);
            offset += q->len;
        }
        LINK_STATS_INC(link.recv);
    } else {
        LINK_STATS_INC(link.memerr);
        LINK_STATS_INC(link.drop);
    }
    return p;
}

// Ініціалізація мережевого інтерфейсу netif
err_t custom_eth_if_init(struct netif *netif) {
    custom_eth_driver_t *drv = (custom_eth_driver_t *)netif->state;
    
    netif->hostname = "lwip_device";
    netif->name[0] = 'e';
    netif->name[1] = 't';
    netif->output = etharp_output;
    netif->linkoutput = low_level_output;
    netif->mtu = 1500;
    netif->flags = NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP | NETIF_FLAG_LINK_UP;
    netif->hwaddr_len = ETHARP_HWADDR_LEN;
    memcpy(netif->hwaddr, drv->mac_addr, ETHARP_HWADDR_LEN);

    return ERR_OK;
}

// Обробник приймального переривання/завдання
void custom_eth_rx_handler(struct netif *netif, uint8_t *buffer, uint16_t len) {
    struct pbuf *p = low_level_input(netif, buffer, len);
    if (p != NULL) {
        // Безпечна передача пакета у потік tcpip_thread
        if (netif->input(p, netif) != ERR_OK) {
            pbuf_free(p);
        }
    }
}
