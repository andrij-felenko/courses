#include "lwip/tcp.h"

static err_t server_recv_cb(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
    if (p == NULL) {
        tcp_close(tpcb);
        return ERR_OK;
    }
    // Обробка даних...
    tcp_recved(tpcb, p->tot_len);
    pbuf_free(p);
    return ERR_OK;
}

static err_t server_accept_cb(void *arg, struct tcp_pcb *newpcb, err_t err) {
    if (err != ERR_OK || newpcb == NULL) return ERR_VAL;
    tcp_arg(newpcb, NULL);
    tcp_recv(newpcb, server_recv_cb);
    return ERR_OK;
}

void start_tcp_server(uint16_t port) {
    struct tcp_pcb *pcb = tcp_new();
    tcp_bind(pcb, IP_ADDR_ANY, port);
    pcb = tcp_listen(pcb);
    tcp_accept(pcb, server_accept_cb);
}
