#include <lwip/pbuf.h>
#include <Arduino.h>

// Клас-обгортка для безпечної роботи з pbuf в Arduino C++
class PbufHandler {
public:
    static void processAndFree(struct pbuf *head) {
        if (!head) return;

        Serial.printf("Початок обробки кадру tot_len = %u байт\n", head->tot_len);
        struct pbuf *curr = head;
        size_t node_index = 0;

        while (curr != nullptr) {
            Serial.printf(" Вузол [%u]: len = %u байт\n", node_index++, curr->len);
            curr = curr->next;
        }

        // Атомарне зменшення лічильника ref та звільнення DRAM
        uint8_t freed = pbuf_free(head);
        Serial.printf("Успішно звільнено вузлів pbuf: %u\n", freed);
    }
};
