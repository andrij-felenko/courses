// AArch64: еквівалентні лямбда-зонди на C++20
inline auto probe_currentel = []() noexcept {
    uint64_t v = 0;
    __asm__ volatile ("mrs %0, CurrentEL" : "=r"(v));
    g_produced = v >> 2;
};
inline auto probe_sctlr = []() noexcept {
    uint64_t v = 0;
    __asm__ volatile ("mrs %0, sctlr_el1" : "=r"(v));
    g_produced = v;
};
inline auto probe_ctr = []() noexcept {
    uint64_t v = 0;
    __asm__ volatile ("mrs %0, ctr_el0" : "=r"(v));
    g_produced = v;
};
inline auto probe_isar0 = []() noexcept {
    uint64_t v = 0;
    __asm__ volatile ("mrs %0, id_aa64isar0_el1" : "=r"(v));
    g_produced = v;
};
