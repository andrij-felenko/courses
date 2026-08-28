#include <sys/mman.h>
#include <iostream>
#include <span>
#include <cstddef>
#include <system_error>

void* raw_ptr = ::mmap(nullptr, 65536, PROT_READ | PROT_WRITE | PROT_MTE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
if (raw_ptr == MAP_FAILED) {
    throw std::system_error(errno, std::generic_category(), "mmap з PROT_MTE зазнав невдачі");
}
std::span<std::byte> mte_buffer(static_cast<std::byte*>(raw_ptr), 65536);
