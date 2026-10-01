#include "lwip/tcp.h"

// Колбек прийому даних у низькорівневому асинхронному API lwIP
err_t recv_callback(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
    if (p == NULL) {
        // Клієнт закрив з'єднання
        tcp_close(tpcb);
        return ERR_OK;
    }

    // Підтверджуємо отримання байтів для зсуву ковзного вікна TCP
    tcp_recved(tpcb, p->tot_len);

    // Обов'язкове вивільнення ланцюжка pbuf після обробки
    pbuf_free(p);
    return ERR_OK;
}
