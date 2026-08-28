#include <vector>
#include <chrono>
#include <cstdint>

namespace hamiltonian {

struct Result {
    Status status{Status::NoCycleExists};
    std::vector<size_t> path{};
    uint64_t states_explored{0};
    std::chrono::duration<double> elapsed_time{0};
};

} // namespace hamiltonian
