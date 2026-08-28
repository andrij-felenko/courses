// benchmark_hugepages.cpp — Ідіоматична реалізація мовою C++23 із використанням RAII та chrono
// _GNU_SOURCE обов'язковий: під суворим -std=c++23 glibc не показує MAP_HUGETLB і MADV_HUGEPAGE
#define _GNU_SOURCE
#include <iostream>
#include <vector>
#include <numeric>
#include <chrono>
#include <memory>
#include <random>
#include <string_view>
#include <expected>
#include <system_error>
#include <cstdint>
#include <cstring>
#include <cerrno>
#include <sys/mman.h>
#include <unistd.h>

namespace memory_bench {

constexpr size_t ALLOC_SIZE = 256 * 1024 * 1024; // 256 МіБ
constexpr size_t NUM_ACCESSES = 10000000;          // 10 млн звернень

enum class AllocationMode {
    Standard4K,
    ThpMadvise,
    Hugetlb2M
};

// RAII-обгортка для безпечного управління пам'яттю mmap
struct MmapDeleter {
    size_t length{0};
    void operator()(uint8_t* ptr) const noexcept {
        if (ptr && ptr != MAP_FAILED) {
            ::munmap(ptr, length);
        }
    }
};

using UniqueMmap = std::unique_ptr<uint8_t[], MmapDeleter>;

// Клас фабрики з виділення пам'яті через std::expected
class MemoryBuffer {
public:
    static std::expected<UniqueMmap, std::string> create(AllocationMode mode) {
        int flags = MAP_PRIVATE | MAP_ANONYMOUS;
        if (mode == AllocationMode::Hugetlb2M) {
            flags |= MAP_HUGETLB | MAP_HUGE_2MB;
        }

        void* raw_ptr = ::mmap(nullptr, ALLOC_SIZE, PROT_READ | PROT_WRITE, flags, -1, 0);
        if (raw_ptr == MAP_FAILED) {
            return std::unexpected("Не вдалося виконати mmap: " + std::string(strerror(errno)));
        }

        auto ptr = static_cast<uint8_t*>(raw_ptr);

        if (mode == AllocationMode::ThpMadvise) {
            if (::madvise(ptr, ALLOC_SIZE, MADV_HUGEPAGE) != 0) {
                std::cerr << "Попередження: madvise(MADV_HUGEPAGE) повернув помилку: " 
                          << strerror(errno) << '\n';
            }
        }

        return UniqueMmap(ptr, MmapDeleter{ALLOC_SIZE});
    }
};

class BenchmarkRunner {
public:
    static void run(std::string_view name, AllocationMode mode) {
        auto result = MemoryBuffer::create(mode);
        if (!result) {
            std::cerr << "[C++] " << name << " -> Помилка: " << result.error() << '\n';
            return;
        }

        auto& buffer = result.value();

        // 1. Прогрів пам'яті через крок у 4 КіБ
        for (size_t i = 0; i < ALLOC_SIZE; i += 4096) {
            buffer[i] = 1;
        }

        // 2. Бенчмарк за допомогою шаблонів chrono та LCG
        uint32_t seed = 0x12345678;
        const size_t mask = ALLOC_SIZE - 1;
        volatile uint64_t sum = 0;

        const auto start = std::chrono::high_resolution_clock::now();

        for (size_t i = 0; i < NUM_ACCESSES; ++i) {
            seed = seed * 1664525u + 1013904223u;
            const size_t index = static_cast<size_t>(seed) & mask;
            sum += buffer[index];
            buffer[index] = static_cast<uint8_t>(sum & 0xFF);
        }

        const auto end = std::chrono::high_resolution_clock::now();
        const std::chrono::duration<double, std::nano> elapsed_ns = end - start;

        const double total_sec = elapsed_ns.count() * 1e-9;
        const double ns_per_access = elapsed_ns.count() / NUM_ACCESSES;

        std::cout << "[C++] " << name << ": Час = " << total_sec 
                  << " сек | Затримка = " << ns_per_access 
                  << " нс/доступ (sum=" << sum << ")\n";
    }
};

} // namespace memory_bench

int main() {
    std::cout << "=== C++ Вимірювач продуктивності пам'яті (256 МіБ) ===\n";
    memory_bench::BenchmarkRunner::run("Стандартні 4K", memory_bench::AllocationMode::Standard4K);
    memory_bench::BenchmarkRunner::run("THP (madvise)", memory_bench::AllocationMode::ThpMadvise);
    memory_bench::BenchmarkRunner::run("HugeTLB (2M)", memory_bench::AllocationMode::Hugetlb2M);
    return 0;
}
