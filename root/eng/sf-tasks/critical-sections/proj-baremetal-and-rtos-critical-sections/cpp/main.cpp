#include <iostream>
#include <cstdint>

class InterruptGuard {
    uint32_t saved_primask;
public:
    InterruptGuard() {
        saved_primask = 0;
        std::cout << "[RAII] Interrupts disabled (CPSID i)\n";
    }
    ~InterruptGuard() {
        std::cout << "[RAII] Interrupts restored (CPSIE i)\n";
    }
    InterruptGuard(const InterruptGuard&) = delete;
    InterruptGuard& operator=(const InterruptGuard&) = delete;
};

int main() {
    std::cout << "=== C++ RAII InterruptGuard Demonstration ===\n";
    {
        InterruptGuard guard;
        std::cout << "Executing critical state updates safely...\n";
    }
    std::cout << "Execution resumed outside critical section.\n";
    return 0;
}
