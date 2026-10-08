#include "lwip/tcp.h"

typedef struct {
    struct tcp_pcb *pcb;
    uint8_t retries;
} session_t;

static void error_cb(void *arg, err_t err) {
    session_t *sess = (session_t *)arg;
    if (sess != NULL) {
        sess->pcb = NULL; // Обнуляємо вказівник, оскільки pcb вже звільнено стеком!
        free(sess);
    }
}

static err_t poll_cb(void *arg, struct tcp_pcb *tpcb) {
    session_t *sess = (session_t *)arg;
    if (sess == NULL) {
        tcp_abort(tpcb);
        return ERR_ABRT;
    }
    sess->retries++;
    if (sess->retries > 10) { // Таймаут 5 секунд
        tcp_abort(tpcb);
        return ERR_ABRT; // Обов'язково повертаємо ERR_ABRT після tcp_abort!
    }
    return ERR_OK;
}

void setup_safety_handlers(struct tcp_pcb *pcb, session_t *sess) {
    sess->pcb = pcb;
    sess->retries = 0;
    tcp_arg(pcb, sess);
    tcp_err(pcb, error_cb);
    tcp_poll(pcb, poll_cb, 1); // Виклик кожні 0.5 секунди
}
