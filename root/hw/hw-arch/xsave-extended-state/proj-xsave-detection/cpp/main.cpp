#include <iostream>
#include <memory>
#include <bitset>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include <cpuid.h>
#include <immintrin.h>

namespace xsave {

constexpr std::size_t Alignment = 64;

/* Структура заголовка XSAVE із гарантованим вирівнюванням */
struct alignas(64) Header {
    std::uint64_t state_bv{0};
    std::uint64_t comp_bv{0};
    std::uint64_t reserved[6]{0};
};

/* Спеціальний функтор видалення пам'яті, виділеної через std::aligned_alloc */
struct AlignedDeleter {
    void operator()(std::uint8_t* ptr) const noexcept {
        std::free(ptr);
    }
};

using BufferPtr = std::unique_ptr<std::uint8_t[], AlignedDeleter>;

class ContextManager {
public:
    ContextManager() {
        std::uint32_t eax{0}, ebx{0}, ecx{0}, edx{0};

        /* 1. Перевірка прапорця OSXSAVE у CPUID.(EAX=1):ECX[27] */
        __cpuid(1, eax, ebx, ecx, edx);
        if (!(ecx & (1u << 27))) {
            throw std::runtime_error("Процесор або ОС не підтримують XSAVE (CR4.OSXSAVE=0)");
        }

        /* 2. Запит розміру кадру для активної конфігурації у CPUID.(EAX=0xD, ECX=0) */
        __cpuid_count(0xD, 0, eax, ebx, ecx, edx);
        buffer_size_ = static_cast<std::size_t>(ebx);

        /* 3. Зчитування активної конфігурації компонентів із XCR0 */
        xcr0_mask_ = readXcr0();

        /* 4. Виділення блоку пам'яті з гарантією вирівнювання за межею 64 байти */
        auto* raw_mem = static_cast<std::uint8_t*>(std::aligned_alloc(Alignment, buffer_size_));
        if (!raw_mem) {
            throw std::bad_alloc();
        }
        buffer_.reset(raw_mem);
        std::memset(buffer_.get(), 0, buffer_size_);
    }

    void saveCurrentState() noexcept {
        const auto eax = static_cast<std::uint32_t>(xcr0_mask_);
        const auto edx = static_cast<std::uint32_t>(xcr0_mask_ >> 32);
        auto* ptr = buffer_.get();

        __asm__ volatile(
            "xsave64 %0"
            : "+m"(*ptr)
            : "a"(eax), "d"(edx)
            : "memory"
        );
    }

    void restoreState() const noexcept {
        const auto eax = static_cast<std::uint32_t>(xcr0_mask_);
        const auto edx = static_cast<std::uint32_t>(xcr0_mask_ >> 32);
        const auto* ptr = buffer_.get();

        __asm__ volatile(
            "xrstor64 %0"
            :
            : "m"(*ptr), "a"(eax), "d"(edx)
            : "memory"
        );
    }

    [[nodiscard]] const Header& getHeader() const noexcept {
        return *reinterpret_cast<const Header*>(buffer_.get() + 512);
    }

    [[nodiscard]] std::size_t size() const noexcept { return buffer_size_; }
    [[nodiscard]] std::uint64_t xcr0() const noexcept { return xcr0_mask_; }

private:
    static std::uint64_t readXcr0() noexcept {
        std::uint32_t eax{0}, edx{0};
        __asm__ volatile("xgetbv" : "=a"(eax), "=d"(edx) : "c"(0));
        return (static_cast<std::uint64_t>(edx) << 32) | eax;
    }

    std::size_t buffer_size_{0};
    std::uint64_t xcr0_mask_{0};
    BufferPtr buffer_{nullptr};
};

} // namespace xsave

int main() {
    try {
        xsave::ContextManager ctx;

        std::cout << "Ініціалізовано контекст XSAVE (C++):\\n"
                  << "  Розмір буфера : " << ctx.size() << " байтів\\n"
                  << "  Маска XCR0    : 0x" << std::hex << ctx.xcr0() << std::dec << "\\n";

        ctx.saveCurrentState();

        const auto& hdr = ctx.getHeader();
        const std::bitset<64> mask(hdr.state_bv);

        std::cout << "\\nАналіз бітової карти XSTATE_BV: 0x" << std::hex << hdr.state_bv << std::dec << "\\n";
        if (mask.test(0)) std::cout << "  - x87 FPU стан активний\\n";
        if (mask.test(1)) std::cout << "  - SSE регістри XMM зафіксовано\\n";
        if (mask.test(2)) std::cout << "  - AVX YMM_Hi128 модифіковано\\n";
        if (mask.test(5)) std::cout << "  - AVX-512 Opmask k0-k7 збережено\\n";
        if (mask.test(6)) std::cout << "  - AVX-512 ZMM_Hi256 збережено\\n";
        if (mask.test(7)) std::cout << "  - AVX-512 Hi16_ZMM збережено\\n";
        if (mask.test(9)) std::cout << "  - PKRU ключі захисту збережено\\n";
        if (mask.test(17) || mask.test(18)) std::cout << "  - AMX матричний стан збережено\\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка роботи з XSAVE: " << ex.what() << "\\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
