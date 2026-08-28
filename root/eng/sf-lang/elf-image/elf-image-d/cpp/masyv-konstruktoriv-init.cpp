#include <cstddef>
#include <span>

extern "C" {
    using InitFunc = void (*)();
    extern InitFunc __init_array_start[];
    extern InitFunc __init_array_end[];
}

void call_global_constructors_cpp() noexcept {
    const std::span<InitFunc> constructors(
        __init_array_start,
        static_cast<std::size_t>(__init_array_end - __init_array_start)
    );

    for (const auto& constructor : constructors) {
        if (constructor != nullptr) {
            constructor();
        }
    }
}
