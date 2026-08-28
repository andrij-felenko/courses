#ifdef DEBUG
struct AllocationCanary {
    static constexpr uint32_t MagicHead = 0xDEADBEEF;
    static constexpr uint32_t MagicTail = 0xCAFEBABE;
    uint32_t head{MagicHead};
};

void* debug_allocate(ThreadLocalArena& arena, std::size_t bytes, std::size_t alignment) {
    std::size_t total_size = sizeof(AllocationCanary) + bytes + sizeof(uint32_t);
    auto* base = static_cast<std::byte*>(arena.allocate(total_size, alignment));
    
    auto* canary = new (base) AllocationCanary();
    auto* user_ptr = base + sizeof(AllocationCanary);
    auto* tail_magic = reinterpret_cast<uint32_t*>(user_ptr + bytes);
    *tail_magic = AllocationCanary::MagicTail;

    return user_ptr;
}

void verify_canary(void* user_ptr, std::size_t bytes) {
    auto* base = static_cast<std::byte*>(user_ptr) - sizeof(AllocationCanary);
    auto* canary = reinterpret_cast<AllocationCanary*>(base);
    auto* tail_magic = reinterpret_cast<uint32_t*>(static_cast<std::byte*>(user_ptr) + bytes);

    if (canary->head != AllocationCanary::MagicHead || *tail_magic != AllocationCanary::MagicTail) {
        std::cerr << "КАТАСТРОФА: Виявлено пошкодження пам'яті (Memory Corruption) в арені!\n";
        std::abort();
    }
}
#endif
