// Простір користувача C++20: періодичне опитування per-CPU BPF мапи
#include <bpf/bpf.h>
#include <vector>
#include <numeric>
#include <iostream>

void read_xdp_metrics(int map_fd, unsigned int num_cpus) {
    std::vector<uint64_t> per_cpu_values(num_cpus);
    std::array<uint64_t, 4> total_counters{0, 0, 0, 0};

    for (uint32_t idx = 0; idx < 4; ++idx) {
        if (bpf_map_lookup_elem(map_fd, &idx, per_cpu_values.data()) == 0) {
            total_counters[idx] = std::accumulate(per_cpu_values.begin(), per_cpu_values.end(), 0ULL);
        }
    }

    const double tn = static_cast<double>(total_counters[0]);
    const double fp = static_cast<double>(total_counters[1]);
    const double fn = static_cast<double>(total_counters[2]);
    const double tp = static_cast<double>(total_counters[3]);
    const double precision = (tp + fp > 0.0) ? (tp / (tp + fp)) : 0.0;
    const double recall    = (tp + fn > 0.0) ? (tp / (tp + fn)) : 0.0;

    std::cout << "[XDP eBPF] Precision: " << precision << " | Recall: " << recall << "\n";
}
