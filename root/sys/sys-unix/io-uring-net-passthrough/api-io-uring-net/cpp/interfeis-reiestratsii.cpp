// cpp
#include <cstdint>

struct IoUringBufReg {
    std::uint64_t ring_addr;    // Адреса кольца io_uring_buf в ОЗП
    std::uint32_t ring_entries; // Кількість буферів (2^N)
    std::uint16_t bgid;         // Buffer Group ID
    std::uint16_t flags;        // Конфігураційні прапорці
    std::uint64_t resv[3];      // Резерв ядра
};
