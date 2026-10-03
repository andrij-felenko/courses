#include "lwip/tcp.h"
#include "lwip/stats.h"
#include "lwip/err.h"

// Статичний масив даних у Flash/ROM (Zero-Copy джерело)
static const char g_rom_page[] = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Zero-Copy LwIP</h1>";

// Калбек відправки даних у RAW API
err_t send_zero_copy_page(struct tcp_pcb *tpcb) {
    // Відправка без прапорця TCP_WRITE_FLAG_COPY (Zero-Copy)
    err_t err = tcp_write(tpcb, g_rom_page, sizeof(g_rom_page) - 1, TCP_WRITE_FLAG_MORE);
    if (err == ERR_OK) {
        tcp_output(tpcb);
    } else if (err == ERR_MEM) {
        // Логування помилки браку пам'яті у буферах
        #if LWIP_STATS
        stats_display_proto(&lwip_stats.memp[MEMP_PBUF_POOL], "PBUF_POOL");
        #endif
    }
    return err;
}

// Моніторинг витоків пам'яті LwIP
void print_lwip_diagnostics(void) {
    #if LWIP_STATS
    printf("PBUF Pool used: %d / %d (Errors: %d)\n",
           lwip_stats.memp[MEMP_PBUF_POOL].used,
           lwip_stats.memp[MEMP_PBUF_POOL].avail,
           lwip_stats.memp[MEMP_PBUF_POOL].err);
           
    printf("TCP PCBs active: %d (Mem errors: %d)\n",
           lwip_stats.memp[MEMP_TCP_PCB].used,
           lwip_stats.memp[MEMP_TCP_PCB].err);
    #endif
}
