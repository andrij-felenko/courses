#include <hwloc.h>
#include <stdio.h>

void print_hwloc_topology(void) {
    hwloc_topology_t topo;
    hwloc_topology_init(&topo);
    hwloc_topology_load(topo);

    // Отримання кількості NUMA-вузлів через тип HWLOC_OBJ_NUMANODE
    int num_nodes = hwloc_get_nbobjs_by_type(topo, HWLOC_OBJ_NUMANODE);
    printf("Виявлено NUMA-вузлів через hwloc: %d\n", num_nodes);

    for (int i = 0; i < num_nodes; ++i) {
        hwloc_obj_t node = hwloc_get_obj_by_type(topo, HWLOC_OBJ_NUMANODE, i);
        printf("  NUMANode #%d: обсяг пам'яті = %.2f ГБ\n",
               node->os_index,
               (double)node->attr->numanode.memory_overhead / (1024 * 1024 * 1024));
    }

    hwloc_topology_destroy(topo);
}
