#include <utility>

/* C++ варіант з поверненням прапорця успіху */
bool check_add_overflow(unsigned long a, unsigned long b, unsigned long &res) noexcept {
    asm volatile goto (
        "addq %[val], %[dest]\n\t"
        "jc %l[overflow_label]"
        : [dest] "+r" (a)
        : [val] "r" (b)
        : "cc"
        : overflow_label
    );
    
    res = a;
    return false;

overflow_label:
    return true;
}
