#include <sys/mman.h>
#include <iostream>
#include <system_error>
#include <cstddef>

int main() {
    constexpr std::size_t size = 10ULL * 1024 * 1024 * 1024; // 10 ГіБ
    void* ptr = ::mmap(nullptr, size, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) {
        throw std::system_error(errno, std::generic_category(), "mmap failed");
    }
    auto* buf = static_cast<volatile char*>(ptr);
    // Фізичної пам'яті виділено: 0 байтів
    buf[0] = 'A'; // Тут виникає #PF: виділяється рівно 4 КіБ
    ::munmap(ptr, size);
    return 0;
}
