#include <iostream>
#include <iomanip>
#include <chrono>
#include <system_error>
#include <sys/mman.h>
#include <sys/resource.h>

constexpr std::size_t PGSZ = 4096;
constexpr std::size_t LEN = 1024UL * 1024 * 1024; // 1 GiB

struct MmapRegion {
    void* ptr{MAP_FAILED};
    std::size_t len{0};

    MmapRegion(std::size_t length, int prot, int flags) : len(length) {
        ptr = mmap(nullptr, len, prot, flags, -1, 0);
        if (ptr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap failed");
        }
    }

    ~MmapRegion() {
        if (ptr != MAP_FAILED) {
            munmap(ptr, len);
        }
    }

    char* get() const { return static_cast<char*>(ptr); }
};

static long minflt() {
    struct rusage ru{};
    getrusage(RUSAGE_SELF, &ru);
    return ru.ru_minflt;
}

int main() {
    try {
        long f0 = minflt();
        auto t0 = std::chrono::steady_clock::now();

        MmapRegion region(LEN, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS);
        auto t1 = std::chrono::steady_clock::now();
        std::chrono::duration<double, std::milli> elapsed_req = t1 - t0;
        std::cout << "запит:           " << std::setw(8) << std::fixed << std::setprecision(3)
                  << elapsed_req.count() << " мс, збоїв " << (minflt() - f0) << "\n";

        f0 = minflt();
        t0 = std::chrono::steady_clock::now();
        char* p = region.get();
        for (std::size_t i = 0; i < LEN; i += PGSZ) p[i] = 1;
        t1 = std::chrono::steady_clock::now();
        std::chrono::duration<double, std::milli> elapsed_touch = t1 - t0;
        long n = minflt() - f0;
        double ns_per_fault = n ? (elapsed_touch.count() * 1e6 / n) : 0.0;
        std::cout << "перший дотик:    " << std::setw(8) << elapsed_touch.count()
                  << " мс, збоїв " << n << ", " << std::setprecision(0) << ns_per_fault << " нс на збій\n";

        f0 = minflt();
        t0 = std::chrono::steady_clock::now();
        for (size_t i = 0; i < LEN; i += PGSZ) p[i] = 2;
        t1 = std::chrono::steady_clock::now();
        std::chrono::duration<double, std::milli> elapsed_second = t1 - t0;
        std::cout << "другий прохід:   " << std::setw(8) << std::setprecision(3)
                  << elapsed_second.count() << " мс, збоїв " << (minflt() - f0) << "\n";
    } catch (const std::exception& e) {
        std::cerr << e.what() << "\n";
        return 1;
    }
    return 0;
}
