#include "dsu.h"
#include <stdio.h>
#include <stdlib.h>

int main(void) {
    const size_t n = 100;
    DSU *dsu = dsu_create(n);
    if (!dsu) {
        fprintf(stderr, "Помилка виділення пам'яті DSU\n");
        return EXIT_FAILURE;
    }

    bool unite_ok = false;
    DSUStatus status = dsu_union(dsu, 10, 20, &unite_ok);
    if (status != DSU_SUCCESS) {
        fprintf(stderr, "Помилка виконанні union: %d\n", status);
        dsu_destroy(dsu);
        return EXIT_FAILURE;
    }

    bool is_conn = false;
    dsu_is_connected(dsu, 10, 20, &is_conn);
    printf("Вузли 10 та 20 зв'язані: %s\n", is_conn ? "так" : "ні");

    dsu_destroy(dsu);
    return EXIT_SUCCESS;
}
