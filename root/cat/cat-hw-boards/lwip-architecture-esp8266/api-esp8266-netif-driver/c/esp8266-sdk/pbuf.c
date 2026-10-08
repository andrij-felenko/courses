#include "lwip/pbuf.h"
#include "lwip/netif.h"

// Низькорівневе відправлення Ethernet-кадру у Wi-Fi MAC
static err_t low_level_output(struct netif *netif, struct pbuf *p) {
    struct pbuf *q;
    uint16_t total_len = p->tot_len;
    uint8_t buffer[1514]; // Тимчасовий плоский буфер для збирання кадру
    uint16_t offset = 0;

    // Збирання розірваних фрагментів pbuf в один суцільний буфер кадру
    for (q = p; q != NULL; q = q->next) {
        memcpy(&buffer[offset], q->payload, q->len);
        offset += q->len;
    }

    // Передача кадру в бінарний драйвер Wi-Fi MAC ESP8266
    if (esp8266_wifi_mac_tx(buffer, total_len) != 0) {
        return ERR_IF; // Помилка мережевого інтерфейсу
    }

    return ERR_OK;
}

// Приклад прийому кадру з преривання Wi-Fi та передача в lwIP
void esp8266_wifi_mac_rx_callback(uint8_t *frame_data, uint16_t frame_len, struct netif *netif) {
    if (frame_len == 0 || frame_data == NULL) return;

    // Виділення нового пакета в пулі пам'яті lwIP
    struct pbuf *p = pbuf_alloc(PBUF_RAW, frame_len, PBUF_POOL);
    if (p != NULL) {
        struct pbuf *q;
        uint16_t offset = 0;
        
        // Заповнення сегментів pbuf даними з апаратного буфера
        for (q = p; q != NULL; q = q->next) {
            memcpy(q->payload, &frame_data[offset], q->len);
            offset += q->len;
        }

        // Передача пакета у стек lwIP (ethernet_input)
        if (netif->input(p, netif) != ERR_OK) {
            pbuf_free(p); // Вивільнення пам'яті у разі відхилення пакета
        }
    }
}
