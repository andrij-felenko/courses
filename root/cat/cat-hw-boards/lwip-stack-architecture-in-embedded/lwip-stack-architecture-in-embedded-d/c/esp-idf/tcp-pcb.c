#include "lwip/tcpip.h"
#include "lwip/tcp.h"
#include "lwip/err.h"

// Калбек, який гарантовано виконується у контексті потоку tcpip_thread
static void deferred_send_cb(void *ctx) {
    struct tcp_pcb *pcb = (struct tcp_pcb *)ctx;
    if (pcb != NULL) {
        const char payload[] = "Data sent from tcpip_thread context";
        tcp_write(pcb, payload, sizeof(payload) - 1, TCP_WRITE_FLAG_COPY);
        tcp_output(pcb);
    }
}

// Завдання RTOS для відправки даних
void app_sender_task(void *pvParameters) {
    struct tcp_pcb *active_pcb = (struct tcp_pcb *)pvParameters;

    // Варіант 1: Безпечна асинхронна відправка через поштову скриньку
    err_t err = tcpip_callback(deferred_send_cb, active_pcb);
    if (err != ERR_OK) {
        // Помилка виділення пам'яті або переповнення mbox
    }

    // Варіант 2: Прямий виклик RAW API через механізм Core Locking
    LOCK_TCPIP_CORE();
    tcp_write(active_pcb, "Direct Data", 11, TCP_WRITE_FLAG_COPY);
    tcp_output(active_pcb);
    UNLOCK_TCPIP_CORE();
}
