#include <hwloc.h>
#include <iostream>
#include <memory>
#include <format>
#include <stdexcept>

struct HwlocTopologyDeleter {
    void operator()(hwloc_topology_t topo) const noexcept {
        if (topo) hwloc_topology_destroy(topo);
    }
};
using UniqueTopology = std::unique_ptr<hwloc_topology, HwlocTopologyDeleter>;

void print_hwloc_topology_cpp() {
    hwloc_topology_t raw_topo;
    if (hwloc_topology_init(&raw_topo) != 0) {
        throw std::runtime_error("hwloc_topology_init failed");
    }
    UniqueTopology topo(raw_topo);
    hwloc_topology_load(topo.get());

    const int num_nodes = hwloc_get_nbobjs_by_type(topo.get(), HWLOC_OBJ_NUMANODE);
    std::cout << std::format("Виявлено NUMA-вузлів через hwloc: {}\n", num_nodes);

    for (int i = 0; i < num_nodes; ++i) {
        const hwloc_obj_t node = hwloc_get_obj_by_type(topo.get(), HWLOC_OBJ_NUMANODE, i);
        std::cout << std::format("  NUMANode #{}: індекс ОС = {}\n", i, node->os_index);
    }
}
