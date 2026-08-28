void broken_stack_usage(int val) noexcept {
    int local_data = val * 10;
    asm volatile (
        "pushq %0\n\t"
        "popq %%rax"
        :
        : "r" (static_cast<uint64_t>(val))
        : "rax"
    );
}
