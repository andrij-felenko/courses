struct alignas(16) Tagged {                // 16 байтів → влазить у cmpxchg16b
    Conn* ptr;
    uintptr_t tag;                         // ← лічильник версій проти ABA
};
std::atomic<Tagged> head;                  // на x86-64 компілюється в дводовгий CAS

Conn* pop() {
    Tagged old = head.load(std::memory_order_acquire), neu;
    do {
        if (!old.ptr) return nullptr;
        neu.ptr = old.ptr->next_free;
        neu.tag = old.tag + 1;             // кожна вдала заміна зсуває версію
    } while (!head.compare_exchange_weak(old, neu,
                 std::memory_order_acquire, std::memory_order_relaxed));
    return old.ptr;
}
