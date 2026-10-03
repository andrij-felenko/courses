#include "lwip/tcp.h"
#include <stdio.h>
#include <string.h>

// Callback прийому даних від віддаленого клієнта
static err_t echo_recv_cb(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
    if (p == NULL) {
        // Клієнт закрив з'єднання (FIN)
        tcp_close(tpcb);
        return ERR_OK;
    }

    // Сповіщення стека про обробку даних для розширення TCP_WND
    tcp_recved(tpcb, p->tot_len);

    // Вхідні дані відправляються назад (ECHO-відповідь)
    tcp_write(tpcb, p->payload, p->len, TCP_WRITE_FLAG_COPY);
    tcp_output(tpcb);

    // Звільнення буфера pbuf з DRAM
    pbuf_free(p);
    return ERR_OK;
}

// Callback прийняття нового з'єднання
static err_t echo_accept_cb(void *arg, struct tcp_pcb *newpcb, err_t err) {
    // Реєстрація обробника прийому даних для нового TCB
    tcp_recv(newpcb, echo_recv_cb);
    return ERR_OK;
}

// Ініціалізація асинхронного сервера на порту 8080
void start_async_tcp_server(void) {
    struct tcp_pcb *server_pcb = tcp_new();
    if (server_pcb != NULL) {
        tcp_bind(server_pcb, IP_ADDR_ANY, 8080);
        server_pcb = tcp_listen(server_pcb);
        tcp_accept(server_pcb, echo_accept_cb);
        printf("Асинхронний TCP-сервер успішно запущено на порту 8080\n");
    }
}
