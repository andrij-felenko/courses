#include <sys/mman.h>
#include <iostream>
#include <memory>
#include <unistd.h>

int main() {
    constexpr size_t size = 100 * 1024 * 1024; // 100 МіБ

    struct MmapDeleter {
        size_t len;
        void operator()(void* p) const {
            if (p && p != MAP_FAILED) munmap(p, len);
        }
    };

    void* raw = mmap(nullptr, size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (raw == MAP_FAILED) return 1;

    std::unique_ptr<void, MmapDeleter> area(raw, MmapDeleter{size});

    if (madvise(area.get(), size, MADV_MERGEABLE) == 0) {
        std::cout << "KSM дозволено для ділянки " << area.get() << "\n";
    }
    return 0;
}
