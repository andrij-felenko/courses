#include <numa.h>
#include <stdio.h>

void configure_nodes(void) {
    // Виділення бітової маски під усі можливі вузли системи
    struct bitmask *nodes = numa_allocate_nodemask();

    // Очищення маски
    numa_bitmask_clearall(nodes);

    // Встановлення бітів для Вузла 0 та Вузла 2
    numa_bitmask_setbit(nodes, 0);
    numa_bitmask_setbit(nodes, 2);

    if (numa_bitmask_isbitset(nodes, 0)) {
        printf("Node 0 обрано для виділення пам'яті\n");
    }

    // Звільнення пам'яті дескриптора маски
    numa_bitmask_free(nodes);
}
