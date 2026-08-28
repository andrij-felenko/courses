// cxl_allocator_bench.cpp
#include <iostream>
#include <memory>
#include <vector>
#include <span>
#include <expected>
#include <chrono>
#include <cstdint>
#include <numeric>
#include <random>
#include <algorithm>
#include <cstring>
#include <numa.h>
#include <numaif.h>
#include <sys/mman.h>
#include <x86intrin.h>

namespace cxl {

enum class AllocationError {
    NumaUnavailable,
    NodeNotFound,
    MmapFailed,
    MbindFailed
};

// C++23 Custom Allocator із підтримкою RAII для CXL NUMA Node
template <typename T>
class CxlDeleter {
    size_t size_bytes_;
public:
    explicit CxlDeleter(size_t size_bytes = 0) : size_bytes_(size_bytes) {}
    void operator()(T* ptr) const noexcept {
        if (ptr && size_bytes_ > 0) {
            munmap(static_cast<void*>(ptr), size_bytes_);
        }
    }
};

template <typename T>
using UniqueCxlPtr = std::unique_ptr<T[], CxlDeleter<T>>;

class CxlMemoryManager {
public:
    static std::expected<int, AllocationError> find_cxl_node() noexcept {
        if (numa_available() < 0) {
            return std::unexpected(AllocationError::NumaUnavailable);
        }

        const int max_node = numa_max_node();
        struct bitmask* cpus = numa_allocate_cpumask();

        for (int n = 0; n <= max_node; ++n) {
            long long free_mem = 0;  // сигнатура: long long numa_node_size64(int, long long *)
            if (numa_node_size64(n, &free_mem) > 0) {
                numa_node_to_cpus(n, cpus);
                if (numa_bitmask_weight(cpus) == 0) {
                    numa_free_cpumask(cpus);
                    return n;
                }
            }
        }

        numa_free_cpumask(cpus);
        return std::unexpected(AllocationError::NodeNotFound);
    }

    template <typename T>
    static std::expected<UniqueCxlPtr<T>, AllocationError> allocate_cxl_span(size_t count, int node) {
        const size_t size_bytes = count * sizeof(T);
        void* addr = mmap(nullptr, size_bytes, PROT_READ | PROT_WRITE,
                          MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
        
        if (addr == MAP_FAILED) {
            return std::unexpected(AllocationError::MmapFailed);
        }

        unsigned long nodemask = (1UL << node);
        if (mbind(addr, size_bytes, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, MPOL_MF_MOVE) < 0) {
            munmap(addr, size_bytes);
            return std::unexpected(AllocationError::MbindFailed);
        }

        // Прогрів сторінок
        std::memset(addr, 0, size_bytes);

        return UniqueCxlPtr<T>(static_cast<T*>(addr), CxlDeleter<T>(size_bytes));
    }
};

class LatencyBenchmark {
public:
    static double run_pointer_chase(std::span<uint64_t> buffer) {
        const size_t count = buffer.size();
        // Перемішування Саттоло: рівно один цикл довжини count, який
        // апаратний prefetcher передбачити не може.
        std::iota(buffer.begin(), buffer.end(), uint64_t{0});
        std::mt19937_64 gen{20240601ULL};
        for (size_t i = count - 1; i > 0; --i) {
            const size_t j = std::uniform_int_distribution<size_t>{0, i - 1}(gen);
            std::swap(buffer[i], buffer[j]);
        }

        uint64_t idx = 0;
        const auto start = std::chrono::high_resolution_clock::now();
        const uint64_t iterations = 10'000'000ULL;

        for (uint64_t i = 0; i < iterations; ++i) {
            idx = buffer[idx];
        }

        const auto end = std::chrono::high_resolution_clock::now();
        const std::chrono::duration<double, std::nano> elapsed = end - start;

        if (idx == 0xFFFFFFFF) std::cout << "checksum: " << idx << '\n';

        return elapsed.count() / static_cast<double>(iterations);
    }
};

} // namespace cxl

int main() {
    auto cxl_node_res = cxl::CxlMemoryManager::find_cxl_node();
    int node = cxl_node_res.value_or(0);
    
    if (cxl_node_res.has_value()) {
        std::cout << "[C++23] Виявлено CXL пам'ять на вузлі: " << node << '\n';
    } else {
        std::cout << "[C++23] CXL вузол не знайдено, використовуємо резервний вузол 0\n";
    }

    constexpr size_t element_count = (1024ULL * 1024ULL * 1024ULL) / sizeof(uint64_t); // 1 ГБ
    auto alloc_res = cxl::CxlMemoryManager::allocate_cxl_span<uint64_t>(element_count, node);

    if (!alloc_res) {
        std::cerr << "Помилка виділення CXL пам'яті!\n";
        return 1;
    }

    auto& cxl_buf = alloc_res.value();
    std::span<uint64_t> buf_span(cxl_buf.get(), element_count);

    double latency_ns = cxl::LatencyBenchmark::run_pointer_chase(buf_span);
    std::cout << "[C++23] Середня затримка CXL RAM: " << latency_ns << " нс\n";

    return 0;
}
