#include <numa.h>
#include <stdio.h>

void setup_node_mask(void) {
    /* Виділення маски потрібного розміру для поточної системи */
    struct bitmask *nodes = numa_allocate_nodemask();

    /* Встановлення бітів вузлів 0 та 1 */
    numa_bitmask_setbit(nodes, 0);
    numa_bitmask_setbit(nodes, 1);

    /* Перевірка біта */
    if (numa_bitmask_isbitset(nodes, 0)) {
        printf("Node 0 active in mask\n");
    }

    /* Звільнення структури */
    numa_free_nodemask(nodes);
}
