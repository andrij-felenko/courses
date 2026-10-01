#include "lwip/tcp.h"

// Колбек обробки фатальних помилок TCP-сокета
void err_callback(void *arg, err_t err) {
    // Стек lwIP самостійно звільняє PCB при помилці,
    // розробник повинен лише обнулити власні вказівники
    struct tcp_pcb **current_pcb = (struct tcp_pcb **)arg;
    if (current_pcb != NULL) {
        *current_pcb = NULL;
    }
}

void setup_resilient_connection(struct tcp_pcb *tpcb) {
    tcp_arg(tpcb, &tpcb);
    tcp_err(tpcb, err_callback);
}
