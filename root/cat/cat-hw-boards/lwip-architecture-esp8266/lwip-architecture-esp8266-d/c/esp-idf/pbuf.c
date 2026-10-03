#include "lwip/pbuf.h"
#include "lwip/err.h"
#include <stdio.h>
#include <string.h>

// Функція демонстрації створення та обробки ланцюжка pbuf у C
void process_pbuf_chain_example(void) {
    // 1. Виділення буфера PBUF_RAM для вихідних даних
    u16_t data_len = 256;
    struct pbuf *p = pbuf_alloc(PBUF_TRANSPORT, data_len, PBUF_RAM);
    if (p == NULL) {
        printf("Помилка ERR_MEM: не вдалося виділити PBUF_RAM у DRAM\n");
        return;
    }

    // 2. Заповнення тестовими даними
    memset(p->payload, 0xAA, p->len);

    // 3. Безпечний обхід ланцюжка pbuf
    u16_t total_bytes = 0;
    for (struct pbuf *q = p; q != NULL; q = q->next) {
        total_bytes += q->len;
        printf("Вузол pbuf: len = %u, payload = %p\n", q->len, q->payload);
    }
    printf("Сумарно оброблено даних: %u байт (tot_len = %u)\n", total_bytes, p->tot_len);

    // 4. Звільнення буфера після завершення роботи
    u8_t dealloc_count = pbuf_free(p);
    printf("Буфер pbuf звільнено, лічильник dealloc: %u\n", dealloc_count);
}
