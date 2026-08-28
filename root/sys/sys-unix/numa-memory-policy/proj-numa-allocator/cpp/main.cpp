#define _GNU_SOURCE
#include <iostream>
#include <vector>
#include <memory>
#include <thread>
#include <span>
#include <chrono>
#include <numeric>
#include <cstring>
#include <pthread.h>
#include <numa.h>
#include <numaif.h>

class NumaBuffer {
public:
    enum class Policy {
        Local,
        OnNode,
        Interleaved
    };

    NumaBuffer(size_t bytes, Policy policy, int target_node = 0)
        : size_(bytes), data_(nullptr)
    {
        switch (policy) {
            case Policy::Local:
                data_ = static_cast<std::byte*>(numa_alloc_local(bytes));
                break;
            case Policy::OnNode:
                data_ = static_cast<std::byte*>(numa_alloc_onnode(bytes, target_node));
                break;
            case Policy::Interleaved:
                data_ = static_cast<std::byte*>(numa_alloc_interleaved(bytes));
                break;
        }
        if (!data_) {
            throw std::bad_alloc();
        }
        // First-touch ініціалізація
        std::memset(data_, 0xAA, size_);
    }

    ~NumaBuffer() noexcept {
        if (data_) {
            numa_free(data_, size_);
        }
    }

    // Заборона копіювання, дозвіл переміщення
    NumaBuffer(const NumaBuffer&) = delete;
    NumaBuffer& operator=(const NumaBuffer&) = delete;
    NumaBuffer(NumaBuffer&& other) noexcept
        : size_(other.size_), data_(other.data_) {
        other.data_ = nullptr;
        other.size_ = 0;
    }
    NumaBuffer& operator=(NumaBuffer&& other) noexcept {
        if (this != &other) {
            if (data_) numa_free(data_, size_);
            data_ = other.data_;
            size_ = other.size_;
            other.data_ = nullptr;
            other.size_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<std::byte> as_span() noexcept {
        return {data_, size_};
    }

    [[nodiscard]] size_t size() const noexcept { return size_; }
    [[nodiscard]] void* data() const noexcept { return data_; }

private:
    size_t size_;
    std::byte* data_;
};

struct BenchmarkResult {
    double elapsed_ms{0.0};
    double bandwidth_gbs{0.0};
};

BenchmarkResult run_memory_benchmark(std::span<std::byte> buffer, int cpu_id, int iterations = 5) {
    // Прив'язка потоку до конкретного процесора
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    auto* uint64_ptr = reinterpret_cast<volatile uint64_t*>(buffer.data());
    size_t count = buffer.size() / sizeof(uint64_t);

    auto start = std::chrono::high_resolution_clock::now();

    for (int it = 0; it < iterations; ++it) {
        volatile uint64_t sum = 0;
        for (size_t i = 0; i < count; i += 8) {
            sum += uint64_ptr[i] + uint64_ptr[i+1] + uint64_ptr[i+2] + uint64_ptr[i+3];
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duration = (end - start) / iterations;

    double total_gigabytes = static_cast<double>(buffer.size()) / (1024.0 * 1024.0 * 1024.0);
    double bw = total_gigabytes / (duration.count() / 1000.0);

    return {duration.count(), bw};
}

int main() {
    if (numa_available() < 0) {
        std::cerr << "NUMA недоступна на цій системі.\n";
        return 1;
    }

    int nodes = numa_num_configured_nodes();
    std::cout << "NUMA-вузлів у системі: " << nodes << "\n";
    if (nodes < 2) {
        std::cout << "Для порівняльного аналізу потрібно щонайменше 2 вузли.\n";
        return 0;
    }

    constexpr size_t buffer_size = 128 * 1024 * 1024; // 128 МіБ
    NumaBuffer buf_node0(buffer_size, NumaBuffer::Policy::OnNode, 0);

    // Отримання CPU для вузлів 0 і 1
    std::unique_ptr<struct bitmask, decltype(&numa_free_cpumask)> cpus_n0(numa_allocate_cpumask(), numa_free_cpumask);
    std::unique_ptr<struct bitmask, decltype(&numa_free_cpumask)> cpus_n1(numa_allocate_cpumask(), numa_free_cpumask);
    numa_node_to_cpus(0, cpus_node0.get());
    numa_node_to_cpus(1, cpus_node1.get());

    int cpu0 = -1, cpu1 = -1;
    for (int i = 0; i < numa_num_configured_cpus(); ++i) {
        if (cpu0 == -1 && numa_bitmask_isbitset(cpus_node0.get(), i)) cpu0 = i;
        if (cpu1 == -1 && numa_bitmask_isbitset(cpus_node1.get(), i)) cpu1 = i;
    }

    BenchmarkResult res_local, res_remote;

    std::jthread t_local([&]() {
        res_local = run_memory_benchmark(buf_node0.as_span(), cpu0);
    });
    t_local.join();

    std::jthread t_remote([&]() {
        res_remote = run_memory_benchmark(buf_node0.as_span(), cpu1);
    });
    t_remote.join();

    std::cout << "Локальний доступ (CPU " << cpu0 << " -> Node 0): "
              << res_local.elapsed_ms << " мс (" << res_local.bandwidth_gbs << " ГБ/с)\n";
    std::cout << "Віддалений доступ (CPU " << cpu1 << " -> Node 0): "
              << res_remote.elapsed_ms << " мс (" << res_remote.bandwidth_gbs << " ГБ/с)\n";

    double penalty = (res_remote.elapsed_ms - res_local.elapsed_ms) / res_local.elapsed_ms * 100.0;
    std::cout << "Штраф за віддалений доступ: +" << penalty << "%\n";

    return 0;
}
