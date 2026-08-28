#include "lwip/opt.h"
#include "lwip/tcp.h"
#include <string.h>

static err_t echo_recv_callback(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
    if (p == NULL) {
        /* Віддалений клієнт закрив з'єднання (FIN) */
        tcp_close(tpcb);
        return ERR_OK;
    }

    if (err != ERR_OK) {
        pbuf_free(p);
        return err;
    }

    /* Підтверджуємо отримання даних стеку для розширення вікна TCP_WND */
    tcp_recved(tpcb, p->tot_len);

    /* Відправляємо отримані дані назад (Ехо) */
    tcp_write(tpcb, p->payload, p->len, TCP_WRITE_FLAG_COPY);
    tcp_output(tpcb);

    pbuf_free(p);
    return ERR_OK;
}

static err_t echo_accept_callback(void *arg, struct tcp_pcb *newpcb, err_t err) {
    if (err != ERR_OK || newpcb == NULL) {
        return ERR_VAL;
    }

    /* Призначаємо зворотний виклик для обробки вхідних даних */
    tcp_recv(newpcb, echo_recv_callback);
    return ERR_OK;
}

void echo_server_init(void) {
    struct tcp_pcb *server_pcb = tcp_new();
    if (server_pcb != NULL) {
        if (tcp_bind(server_pcb, IP_ADDR_ANY, 7) == ERR_OK) {
            server_pcb = tcp_listen(server_pcb);
            tcp_accept(server_pcb, echo_accept_callback);
        } else {
            memp_free(MEMP_TCP_PCB, server_pcb);
        }
    }
}
