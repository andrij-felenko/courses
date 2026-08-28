#include <chrono>
#include <cstddef>

namespace hamiltonian {

struct Config {
    Algorithm algorithm{Algorithm::Auto};
    std::chrono::milliseconds timeout{0};
    size_t max_memory_bytes{0};
    bool find_all_cycles{false};
    bool enable_dirac_check{true};
    int num_threads{1};
};

} // namespace hamiltonian
