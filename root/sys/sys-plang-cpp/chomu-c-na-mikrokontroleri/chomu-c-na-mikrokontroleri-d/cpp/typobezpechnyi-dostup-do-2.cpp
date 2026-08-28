// Доступ до регістрів мовою C++ через шаблони та політики
#include <cstdint>

enum class Access { ReadOnly, WriteOnly, ReadWrite };

template <uintptr_t Addr, typename T, Access Mode>
struct MmioRegister {
    static inline T read() noexcept requires (Mode == Access::ReadOnly || Mode == Access::ReadWrite) {
        return *reinterpret_cast<volatile T*>(Addr);
    }

    static inline void write(T val) noexcept requires (Mode == Access::WriteOnly || Mode == Access::ReadWrite) {
        *reinterpret_cast<volatile T*>(Addr) = val;
    }
};

using GpioA_Moder = MmioRegister<0x40020000UL, uint32_t, Access::ReadWrite>;
using GpioA_Idr   = MmioRegister<0x40020010UL, uint32_t, Access::ReadOnly>;

void safe_cpp_code() {
    GpioA_Moder::write(0x400); // Коректно: регістр підтримує запис
    // GpioA_Idr::write(0x1234); 
    // ПОМИЛКА КОМПІЛЯЦІЇ: концепція requires не задоволена!
}
