#include <stdio.h>
#include "cantor_pairing.h"

/* Сценарій C99: Серіалізація та валідація ребра орієнтованого графа */
void process_graph_edge(uint32_t u, uint32_t v) {
    uint64_t edge_key;
    cantor_status_t status = cantor_encode32(u, v, &edge_key);

    if (status == CANTOR_SUCCESS) {
        printf("Ребро (%u -> %u) закодовано у ключ: %llu\n", u, v, (unsigned long long)edge_key);

        /* Відновлення координат для верифікації */
        cantor_pair32_t recovered;
        if (cantor_decode32(edge_key, &recovered) == CANTOR_SUCCESS) {
            printf("Відновлено ребро: (%u -> %u)\n", recovered.x, recovered.y);
        }
    } else if (status == CANTOR_ERR_OVERFLOW) {
        fprintf(stderr, "Помилка: переповнення розрядності для вершин (%u, %u)\n", u, v);
    }
}
