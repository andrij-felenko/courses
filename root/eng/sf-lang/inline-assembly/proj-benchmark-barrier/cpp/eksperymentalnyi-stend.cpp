#include <span>
#include <cstdint>

/* C++ варіант з безпечним інтерфейсом std::span */
void process_with_barrier(std::span<int> buffer) noexcept {
    int val = 0;
    for (int &elem : buffer) {
        elem = val++ * 2;
        /* Програмний бар'єр інвалідує кешовані значення в регістрах */
        asm volatile ("" ::: "memory");
    }
}

void process_without_barrier(std::span<int> buffer) noexcept {
    int val = 0;
    for (int &elem : buffer) {
        elem = val++ * 2;
    }
}
