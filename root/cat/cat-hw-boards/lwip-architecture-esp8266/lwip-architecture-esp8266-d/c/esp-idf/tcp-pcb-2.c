#include "lwip/tcp.h"
#include <stdio.h>
#include <string.h>

// Обробник прийому даних із підтвердженням ковзного вікна
static err_t flow_control_recv_cb(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
    if (p == NULL) {
        // Одержувач закрив з'єднання
        tcp_close(tpcb);
        return ERR_OK;
    }

    // 1. Отримання довжини вхідних даних
    u16_t bytes_received = p->tot_len;
    printf("Отримано %u байт даних. Поточне вікно rcv_wnd: %u байт\n", bytes_received, tpcb->rcv_wnd);

    // 2. Інформування lwIP про звільнення пам'яті та розширення вікна TCP_WND
    tcp_recved(tpcb, bytes_received);

    // 3. Перевірка доступного місця у буфері відправки перед надсиланням відповіді
    u16_t free_snd_buf = tcp_sndbuf(tpcb);
    if (free_snd_buf >= 128) {
        const char *reply = "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK";
        tcp_write(tpcb, reply, strlen(reply), TCP_WRITE_FLAG_COPY);
        tcp_output(tpcb);
    }

    // 4. Обов'язкове звільнення pbuf для повернення у пул
    pbuf_free(p);
    return ERR_OK;
}
