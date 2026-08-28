#include <iostream>
#include <vector>
#include <chrono>
#include <memory>
#include <span>
#include <random>
#include <numeric>
#include <format>
#include <stdexcept>
#include <sched.h>
#include <numa.h>
#include <numaif.h>

template <typename T>
class NumaBuffer {
public:
    NumaBuffer(std::size_t count, int node)
        : count_(count), node_(node), bytes_(count * sizeof(T)) {
        void *ptr = numa_alloc_onnode(bytes_, node_);
        if (!ptr) {
            throw std::runtime_error(std::format("Не вдалося виділити пам'ять на NUMA-вузлі {}", node_));
        }
        data_ = static_cast<T *>(ptr);
    }

    ~NumaBuffer() noexcept {
        if (data_) numa_free(data_, bytes_);
    }

    NumaBuffer(const NumaBuffer &) = delete;
    NumaBuffer &operator=(const NumaBuffer &) = delete;

    NumaBuffer(NumaBuffer &&other) noexcept
        : data_(other.data_), count_(other.count_), node_(other.node_), bytes_(other.bytes_) {
        other.data_ = nullptr;
        other.count_ = 0;
    }

    NumaBuffer &operator=(NumaBuffer &&other) noexcept {
        if (this != &other) {
            if (data_) numa_free(data_, bytes_);
            data_ = other.data_;
            count_ = other.count_;
            node_ = other.node_;
            bytes_ = other.bytes_;
            other.data_ = nullptr;
            other.count_ = 0;
        }
        return *this;
    }

    [[nodiscard]] std::span<T> span() noexcept { return std::span<T>(data_, count_); }
    [[nodiscard]] std::span<const T> span() const noexcept { return std::span<const T>(data_, count_); }
    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] int node() const noexcept { return node_; }

private:
    T *data_{nullptr};
    std::size_t count_{0};
    int node_{0};
    std::size_t bytes_{0};
};

void pin_thread_to_node(int node) {
    struct bitmask *cpus = numa_allocate_cpumask();
    if (numa_node_to_cpus(node, cpus) != 0) {
        numa_bitmask_free(cpus);
        throw std::runtime_error("numa_node_to_cpus failed");
    }

    int target_cpu = -1;
    for (unsigned int i = 0; i < cpus->size; ++i) {
        if (numa_bitmask_isbitset(cpus, i)) {
            target_cpu = static_cast<int>(i);
            break;
        }
    }
    numa_bitmask_free(cpus);

    if (target_cpu < 0) {
        throw std::runtime_error(std::format("На NUMA-вузлі {} не знайдено активних ядер", node));
    }

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(target_cpu, &cpuset);

    if (sched_setaffinity(0, sizeof(cpu_set_t), &cpuset) != 0) {
        throw std::runtime_error(std::format("sched_setaffinity failed для ЦП {}", target_cpu));
    }
}

double benchmark_bandwidth(std::span<const std::uint64_t> data, int iterations = 5) {
    std::uint64_t sink = 0;
    const auto start = std::chrono::high_resolution_clock::now();

    for (int iter = 0; iter < iterations; ++iter) {
        for (std::size_t i = 0; i < data.size(); i += 8) {
            sink += data[i];
        }
    }

    const auto finish = std::chrono::high_resolution_clock::now();
    const std::chrono::duration<double> elapsed = finish - start;

    if (sink == 0xdeadbeef) std::cout << "Sink\n";

    double total_bytes = static_cast<double>(data.size_bytes()) * iterations;
    return (total_bytes / elapsed.count()) / (1024.0 * 1024.0 * 1024.0); // ГБ/с
}

double benchmark_latency(std::span<const std::uint32_t> indices, std::size_t steps = 20'000'000) {
    std::uint32_t current = 0;
    const auto start = std::chrono::high_resolution_clock::now();

    for (std::size_t s = 0; s < steps; ++s) {
        current = indices[current];
    }

    const auto finish = std::chrono::high_resolution_clock::now();
    const std::chrono::duration<double, std::nano> elapsed = finish - start;

    if (current == 0xdeadbeef) std::cout << "Sink\n";

    return elapsed.count() / static_cast<double>(steps); // наносекунд
}

int main() {
    try {
        if (numa_available() < 0) {
            std::cerr << "Помилка: NUMA не підтримується на цій системі.\n";
            return 1;
        }

        const int max_node = numa_max_node();
        std::cout << std::format("Доступно NUMA-вузлів: {}\n", max_node + 1);

        if (max_node < 1) {
            std::cout << "Для повноцінного тесту потрібно щонайменше 2 вузли.\n";
            return 0;
        }

        constexpr std::size_t bw_elements = (256 * 1024 * 1024) / sizeof(std::uint64_t);
        constexpr std::size_t lat_elements = 4 * 1024 * 1024; // 4M індексів

        NumaBuffer<std::uint64_t> bw_buffer(bw_elements, 0);
        NumaBuffer<std::uint32_t> lat_buffer(lat_elements, 0);

        // Ініціалізація буфера пропускної здатності
        auto bw_span = bw_buffer.span();
        for (std::size_t i = 0; i < bw_span.size(); ++i) {
            bw_span[i] = i ^ 0x5555555555555555ULL;
        }

        // Побудова графа випадкових стрибків для перевірки затримки
        constexpr std::size_t stride = 16; // 64 байти
        const std::size_t num_lines = lat_elements / stride;
        std::vector<std::size_t> perm(num_lines);
        std::iota(perm.begin(), perm.end(), 0);

        std::mt19937_64 rng(42);
        std::shuffle(perm.begin(), perm.end(), rng);

        auto lat_span = lat_buffer.span();
        for (std::size_t i = 0; i < num_lines; ++i) {
            const std::size_t curr = perm[i] * stride;
            const std::size_t next = perm[(i + 1) % num_lines] * stride;
            lat_span[curr] = static_cast<std::uint32_t>(next);
        }

        // Локальний тест
        pin_thread_to_node(0);
        std::cout << "\n=== Тест 1: Локальний доступ (ЦП 0 -> RAM 0) ===\n";
        const double loc_bw = benchmark_bandwidth(bw_buffer.span());
        std::cout << std::format("  Пропускна здатність : {:.2f} ГБ/с\n", loc_bw);
        const double loc_lat = benchmark_latency(lat_buffer.span());
        std::cout << std::format("  Затримка (Pointer Chase) : {:.2f} нс\n", loc_lat);

        // Віддалений тест
        pin_thread_to_node(1);
        std::cout << "\n=== Тест 2: Віддалений доступ (ЦП 1 -> RAM 0) ===\n";
        const double rem_bw = benchmark_bandwidth(bw_buffer.span());
        std::cout << std::format("  Пропускна здатність : {:.2f} ГБ/с\n", rem_bw);
        const double rem_lat = benchmark_latency(lat_buffer.span());
        std::cout << std::format("  Затримка (Pointer Chase) : {:.2f} нс\n", rem_lat);

        // Результати
        std::cout << "\n=== Підсумок NUMA Ratio ===\n";
        std::cout << std::format("  Відношення пропускної здатності : {:.2f}×\n", loc_bw / rem_bw);
        std::cout << std::format("  Відношення затримок доступу      : {:.2f}× (штраф +{:.1f} нс)\n",
                                 rem_lat / loc_lat, rem_lat - loc_lat);

    } catch (const std::exception &ex) {
        std::cerr << std::format("Виняток: {}\n", ex.what());
        return 1;
    }
    return 0;
}
