#include <cstddef>
#include <span>

/* Ідіоматичний виклик списку конструкторів у C++ */
using InitFunction = void (*)(void);

extern "C" {
    extern InitFunction __init_array_start[];
    extern InitFunction __init_array_end[];
}

namespace mcu::runtime {
    inline void call_global_constructors() noexcept {
        const std::span<InitFunction> constructors(
            __init_array_start,
            static_cast<std::size_t>(__init_array_end - __init_array_start)
        );

        for (const auto ctor : constructors) {
            if (ctor != nullptr) {
                ctor();
            }
        }
    }
}
