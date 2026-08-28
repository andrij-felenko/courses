#define _GNU_SOURCE
#include <iostream>
#include <cstring>
#include <memory>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/prctl.h>

#ifndef PR_SET_MEMORY_MERGE
#define PR_SET_MEMORY_MERGE 67
#define PR_GET_MEMORY_MERGE 68
#endif

class MmapRegion {
    void *addr_{MAP_FAILED};
    size_t len_{0};
public:
    explicit MmapRegion(size_t len) : len_(len) {
        addr_ = mmap(nullptr, len_, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    }
    ~MmapRegion() {
        if (addr_ != MAP_FAILED) munmap(addr_, len_);
    }
    MmapRegion(const MmapRegion&) = delete;
    MmapRegion& operator=(const MmapRegion&) = delete;

    void* get() const { return addr_; }
    size_t size() const { return len_; }
    bool valid() const { return addr_ != MAP_FAILED; }
};

int main() {
    constexpr size_t len = 64u << 20;   // 64 МіБ
    MmapRegion region(len);
    if (!region.valid()) {
        std::perror("mmap");
        return 1;
    }

    std::memset(region.get(), 0xA5, region.size());

    if (madvise(region.get(), region.size(), MADV_MERGEABLE) != 0) {
        std::perror("madvise");
        return 1;
    }

    if (prctl(PR_SET_MEMORY_MERGE, 1, 0, 0, 0) != 0) {
        std::perror("prctl");
    }

    std::cout << "pid=" << getpid() << " addr=" << region.get() << std::endl;
    pause();
    return 0;
}
