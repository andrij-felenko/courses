void* operator new(std::size_t n) {
    wire().tick();
    void* p = std::malloc(n ? n : 1);
    if (!p) throw std::bad_alloc{};
    ++tally().taken;
    return p;
}
void operator delete(void* p) noexcept {
    if (!p) return;
    ++tally().given;
    std::free(p);
}
void operator delete(void* p, std::size_t) noexcept { ::operator delete(p); }
