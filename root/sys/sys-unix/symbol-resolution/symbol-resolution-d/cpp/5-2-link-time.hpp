#include <iostream>
#include <cstdlib>

extern "C" {
    void* __real_malloc(std::size_t size);
    
    /* Перехоплювач на етапі компонування у C++ */
    void* __wrap_malloc(std::size_t size) noexcept {
        std::cerr << "[link-time wrap] malloc(" << size << ")\n";
        return __real_malloc(size);
    }
}
