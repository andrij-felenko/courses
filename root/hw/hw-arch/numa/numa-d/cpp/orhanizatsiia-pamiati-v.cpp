// Простір користувача C++: об'єктна модель дескриптора NUMA-вузла
#include <string>
#include <vector>
#include <cstdint>

struct NumaNodeDescriptor {
    int node_id{0};
    std::uint64_t total_memory_bytes{0};
    std::uint64_t free_memory_bytes{0};
    std::vector<int> associated_cpu_ids;
    std::vector<int> relative_distances;
};
