#include <string.h>

#include "ethernetif.h"
#include "eth_dma.h"

#include "lwip/opt.h"
#include "lwip/pbuf.h"
#include "lwip/sys.h"
#include "netif/etharp.h"

#define IFNAME0 'e'
#define IFNAME1 'n'

#define ETHIF_THREAD_STACKSIZE  1024
#define ETHIF_THREAD_PRIO       (TCPIP_THREAD_PRIO + 1)

/* Та сама адреса, що записана в MACA0HR/MACA0LR під час ініціалізації MAC. */
static const uint8_t s_mac_addr[ETH_HWADDR_LEN] = { 0x02, 0x00, 0x00, 0x11, 0x22, 0x33 };

static sys_sem_t rx_ready;

void ethernetif_notify_from_isr(void)
{
    /* Порт lwIP мусить мати ISR-безпечний sys_sem_signal (у FreeRTOS-порті це
       xSemaphoreGiveFromISR). Нічого важчого з переривання ми не робимо. */
    sys_sem_signal(&rx_ready);
}

/* Вихід кадру зі стека просто в кільце DMA — без проміжного буфера. */
static err_t low_level_output(struct netif *netif, struct pbuf *p)
{
    LWIP_UNUSED_ARG(netif);

    if (eth_dma_tx_send(p)) {
        return ERR_OK;
    }
    /* Кільце зайняте. ERR_MEM для стека означає «спробуй пізніше»: TCP
       перешле сегмент сам, датаграма UDP просто загубиться. */
    return ERR_MEM;
}

/* Окрема задача: тут можна виділяти й звільняти pbuf, тут же живе netif->input. */
static void ethernetif_input_thread(void *arg)
{
    struct netif *netif = (struct netif *)arg;

    for (;;) {
        /* Таймаут навмисний: якщо сигнал переривання загубився (наприклад,
           кільце стало вільним у момент RBUS), кільце все одно розгребеться. */
        (void)sys_arch_sem_wait(&rx_ready, 100);

        struct pbuf *p;
        while ((p = eth_dma_rx_receive()) != NULL) {
            if (netif->input(p, netif) != ERR_OK) {
                /* Стек кадр не взяв — звільняє той, хто його дістав. */
                pbuf_free(p);
            }
        }

        /* Заразом віддаємо в пул те, що вже пішло в кабель: якщо трафік
           односторонній, наступного eth_dma_tx_send можна чекати довго. */
        eth_dma_tx_reclaim();
    }
}

err_t ethernetif_init(struct netif *netif)
{
    LWIP_ASSERT("netif != NULL", netif != NULL);

#if LWIP_NETIF_HOSTNAME
    netif->hostname = "lwip-zc";
#endif
    netif->name[0] = IFNAME0;
    netif->name[1] = IFNAME1;
    netif->output = etharp_output;
    netif->linkoutput = low_level_output;
    netif->mtu = 1500;
    netif->hwaddr_len = ETH_HWADDR_LEN;
    memcpy(netif->hwaddr, s_mac_addr, ETH_HWADDR_LEN);
    netif->flags = NETIF_FLAG_BROADCAST | NETIF_FLAG_ETHARP | NETIF_FLAG_LINK_UP;

    if (sys_sem_new(&rx_ready, 0) != ERR_OK) {
        return ERR_MEM;
    }

    /* Порядок важливий: семафор мусить існувати раніше, ніж дозволено
       переривання ETH, — інакше перший же кадр сигналить у порожнечу. */
    if (!eth_dma_init()) {
        sys_sem_free(&rx_ready);
        return ERR_MEM;  /* PBUF_POOL не дав буферів під усе кільце прийому */
    }

    sys_thread_new("ethif", ethernetif_input_thread, netif,
                   ETHIF_THREAD_STACKSIZE, ETHIF_THREAD_PRIO);
    return ERR_OK;
}
