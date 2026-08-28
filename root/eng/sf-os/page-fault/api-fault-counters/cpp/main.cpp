#include <iostream>
#include <system_error>
#include <sys/mman.h>
#include <sys/resource.h>

int main() {
    struct rusage a{}, b{};
    std::size_t len = 64UL << 20; // 64 MiB

    getrusage(RUSAGE_SELF, &a);

    void* ptr = mmap(nullptr, len, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) {
        std::cerr << "mmap failed\n";
        return 1;
    }

    auto* p = static_cast<char*>(ptr);
    for (std::size_t i = 0; i < len; i += 4096) {
        p[i] = 1;
    }

    getrusage(RUSAGE_SELF, &b);
    std::cout << "дрібних " << (b.ru_minflt - a.ru_minflt)
              << ", великих " << (b.ru_majflt - a.ru_majflt) << "\n";

    munmap(ptr, len);
    return 0;
}
