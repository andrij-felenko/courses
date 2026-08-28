#include <numa.h>
#include <stdexcept>
#include <format>

class NumaThreadAffinityManager {
public:
    static void bind_current_thread_to_node(int node) {
        if (numa_run_on_node(node) != 0) {
            throw std::runtime_error(std::format("Не вдалося прив'язати потік до вузла {}", node));
        }
    }
    static void set_preferred_memory_node(int node) noexcept {
        numa_set_preferred(node);
    }
};
