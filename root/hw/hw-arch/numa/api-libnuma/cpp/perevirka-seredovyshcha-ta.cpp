#include <numa.h>
#include <stdexcept>
#include <format>
#include <utility>

class NumaTopologyInspector {
public:
    static bool is_supported() noexcept { return numa_available() >= 0; }
    static int get_max_node() noexcept { return numa_max_node(); }
    static int get_configured_nodes() noexcept { return numa_num_configured_nodes(); }
    static int get_configured_cpus() noexcept { return numa_num_configured_cpus(); }
    static int get_node_distance(int from, int to) noexcept { return numa_distance(from, to); }
};
