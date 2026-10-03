#include "lwip/stats.h"
#include "lwip/tcp.h"
#include <stdio.h>

// Функція діагностики стану пам'яті та пулів lwIP у C
void print_lwip_diagnostics(void) {
#if LWIP_STATS
    printf("=== ДІАГНОСТИКА ПАМ'ЯТІ LWIP ===\n");
    printf("Купа DRAM (mem): Аварійно: %u, Використано: %u, Пік: %u, Всього: %u\n",
           lwip_stats.mem.err, lwip_stats.mem.used, lwip_stats.mem.max, lwip_stats.mem.avail);

    printf("Пул PBUF_POOL : Помилок: %u, Використано: %u, Пік: %u, Всього: %u\n",
           lwip_stats.memp[MEMP_PBUF_POOL]->err,
           lwip_stats.memp[MEMP_PBUF_POOL]->used,
           lwip_stats.memp[MEMP_PBUF_POOL]->max,
           lwip_stats.memp[MEMP_PBUF_POOL]->avail);

    printf("Пул TCP_PCB   : Помилок: %u, Використано: %u, Пік: %u, Всього: %u\n",
           lwip_stats.memp[MEMP_TCP_PCB]->err,
           lwip_stats.memp[MEMP_TCP_PCB]->used,
           lwip_stats.memp[MEMP_TCP_PCB]->max,
           lwip_stats.memp[MEMP_TCP_PCB]->avail);
#else
    printf("Систему статистики LWIP_STATS не активовано в lwipopts.h\n");
#endif
}

// Примусове анулювання завислої TCP-сесії
void force_abort_stuck_pcb(struct tcp_pcb *pcb) {
    if (pcb != NULL) {
        printf("Примусове анулювання завислого з'єднання TCB...\n");
        tcp_abort(pcb); // Надсилає RST та негайно звільняє пам'ять TCB
    }
}
