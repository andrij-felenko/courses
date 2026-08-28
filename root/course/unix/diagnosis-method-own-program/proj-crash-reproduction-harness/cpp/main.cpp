#include <iostream>
#include <string_view>
#include <memory>
#include <vector>
#include <span>
#include <cstring>
#include <climits>
#include <cassert>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

namespace crash_harness {

void trigger_null_dereference() {
    volatile int* ptr = nullptr;
    *ptr = 42;
}

void trigger_rodata_write() {
    constexpr std::string_view ro_str = "Read-only literal string";
    auto* writable = const_cast<char*>(ro_str.data());
    writable[0] = 'W';
}

void trigger_mmap_truncate() {
    char filename[] = "/tmp/crash_mmap_cpp_XXXXXX";
    int fd = mkstemp(filename);
    if (fd < 0) return;

    constexpr size_t page_size = 4096;
    if (ftruncate(fd, page_size) != 0) {
        close(fd);
        unlink(filename);
        return;
    }

    auto* mapped = static_cast<char*>(mmap(nullptr, page_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
    if (mapped == MAP_FAILED) {
        close(fd);
        unlink(filename);
        return;
    }

    mapped[0] = 'A';
    if (ftruncate(fd, 0) != 0) {
        /* Ігноруємо усічення */
    }

    volatile char val = mapped[128];
    (void)val;

    munmap(mapped, page_size);
    close(fd);
    unlink(filename);
}

void trigger_unaligned_access() {
#if defined(__x86_64__) || defined(_M_X64)
    alignas(64) char buffer[64]{};
    char* unaligned_ptr = buffer + 1;
    __asm__ volatile (
        "movdqa (%0), %%xmm0"
        :
        : "r" (unaligned_ptr)
        : "xmm0"
    );
#else
    char buffer[16]{};
    auto* ptr = reinterpret_cast<volatile long*>(buffer + 1);
    *ptr = 0xDEADBEEF;
#endif
}

void trigger_abort_assert() {
    int invariant = 0;
    assert(invariant == 1);
}

void trigger_divide_by_zero(int mode) {
    if (mode == 0) {
        volatile int zero = 0;
        volatile int result = 100 / zero;
        (void)result;
    } else {
        volatile int min_val = INT_MIN;
        volatile int divisor = -1;
        volatile int result = min_val / divisor;
        (void)result;
    }
}

void trigger_use_after_free() {
    auto chunk = std::make_unique<std::vector<int>>(100, 42);
    int* dangling_ref = &(*chunk)[0];
    chunk.reset(); /* Звільняємо пам'ять вектора */
    *dangling_ref = 999; /* Звернення після звільнення */
    std::cout << "Dangling value: " << *dangling_ref << "\n";
}

} // namespace crash_harness

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <1-7>\n"
                  << " 1: SIGSEGV (NULL dereference)\n"
                  << " 2: SIGSEGV (Write to .rodata)\n"
                  << " 3: SIGBUS  (mmap truncate)\n"
                  << " 4: SIGBUS  (unaligned SSE load)\n"
                  << " 5: SIGABRT (assert failure)\n"
                  << " 6: SIGFPE  (divide by zero / overflow)\n"
                  << " 7: Use-After-Free\n";
        return 1;
    }

    int choice = std::stoi(argv[1]);
    switch (choice) {
        case 1: crash_harness::trigger_null_dereference(); break;
        case 2: crash_harness::trigger_rodata_write(); break;
        case 3: crash_harness::trigger_mmap_truncate(); break;
        case 4: crash_harness::trigger_unaligned_access(); break;
        case 5: crash_harness::trigger_abort_assert(); break;
        case 6: crash_harness::trigger_divide_by_zero(0); break;
        case 7: crash_harness::trigger_use_after_free(); break;
        default:
            std::cerr << "Невідомий сценарій: " << choice << "\n";
            return 1;
    }
    return 0;
}
