#include <sys/mman.h>
#include <system_error>
#include <cstddef>

/* Ідіоматичне відображення регіону пам'яті в C++ з контролем помилок через винятки */
void* map_guest_region(std::size_t size, std::size_t offset, int fd) {
    void* addr = ::mmap(nullptr, size + offset,
                        PROT_READ | PROT_WRITE, MAP_SHARED,
                        fd, 0);
    if (addr == MAP_FAILED) {
        throw std::system_error(errno, std::generic_category(), "Помилка mmap регіону");
    }
    return addr;
}
