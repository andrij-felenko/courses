#include "lwip/pbuf.h"
#include "lwip/sys.h"

void process_rx_frame(uint8_t *raw_data, size_t data_len) {
    // Виділення pbuf із статичного пулу PBUF_POOL для прийому даних
    struct pbuf *p = pbuf_alloc(PBUF_RAW, (u16_t)data_len, PBUF_POOL);
    if (p != NULL) {
        // Заповнення буфера даними з апаратного контролера
        pbuf_take(p, raw_data, (u16_t)data_len);

        // Збільшення лічильника ref перед передачею в асинхронний модуль-чергу
        pbuf_ref(p); // ref стає рівним 2

        // Звільнення буфера локальним контекстом
        pbuf_free(p); // ref зменшується до 1, пам'ять не звільняється
        
        // Звільнення буфера приймальним модулем після обробки
        pbuf_free(p); // ref стає 0, буфер повертається в пул PBUF_POOL
    }
}
