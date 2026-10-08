#include "lwip/netif.h"
#include "lwip/sys.h"

#define MAX_TX_RETRIES 3

static err_t robust_low_level_output(struct netif *netif, struct pbuf *p) {
    // Перевірка готовності фізичного каналу
    if (!netif_is_link_up(netif)) {
        return ERR_RTE; // Помилка маршрутизації: немає фіз. зв'язку
    }

    // Блокування ядра lwIP при роботі в багатопотоковому середовищі FreeRTOS
    SYS_ARCH_DECL_PROTECT(lev);
    SYS_ARCH_PROTECT(lev);

    uint8_t retries = 0;
    bool sent_successfully = false;

    while (retries < MAX_TX_RETRIES && !sent_successfully) {
        if (esp8266_wifi_mac_tx_ready()) {
            if (esp8266_wifi_mac_send_pbuf(p) == 0) {
                sent_successfully = true;
            }
        }
        if (!sent_successfully) {
            retries++;
            // Коротка затримка без блокування контексту переривань
            sys_arch_msleep(1);
        }
    }

    SYS_ARCH_UNPROTECT(lev);

    if (!sent_successfully) {
        // Сигнал стеку lwIP про вичерпання буферів передавача
        return ERR_MEM;
    }

    return ERR_OK;
}
