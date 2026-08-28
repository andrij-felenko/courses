#include <cstdint>

struct VhostUserVringAddr {
    uint32_t index{0};           // Індекс черги
    uint32_t flags{0};           // Прапорці конфігурації
    uint64_t desc_user_addr{0};  // Адреса Descriptor Table у QEMU HVA
    uint64_t used_user_addr{0};  // Адреса Used Ring у QEMU HVA
    uint64_t avail_user_addr{0}; // Адреса Avail Ring у QEMU HVA
    uint64_t log_guest_addr{0};  // Адреса для логування під час міграції
};
