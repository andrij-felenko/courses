#include "cmsis_compiler.h"
#include <cstdint>
#include <span>

namespace embedded {

/*
 * Ідіоматичний C++20 RAII-вартовий критичної секції.
 * [[nodiscard]] забороняє створення безіменного тимчасового об'єкта (наприклад, CriticalSectionGuard();),
 * який би миттєво знищився в тому ж рядку, залишивши наступний код незахищеним.
 */
class [[nodiscard]] CriticalSectionGuard {
public:
    CriticalSectionGuard() noexcept : saved_primask_(__get_PRIMASK()) {
        __disable_irq();
        __asm volatile("" ::: "memory");
    }

    ~CriticalSectionGuard() noexcept {
        __asm volatile("" ::: "memory");
        __set_PRIMASK(saved_primask_);
    }

    // Забороняємо копіювання та переміщення
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard(CriticalSectionGuard&&) = delete;
    CriticalSectionGuard& operator=(CriticalSectionGuard&&) = delete;

private:
    std::uint32_t saved_primask_;
};

} // namespace embedded

// Безпечне використання у прикладній функції:
int process_sensor_buffer_cpp(std::span<std::uint8_t> buffer) noexcept {
    const embedded::CriticalSectionGuard lock; // Вхід у критичну секцію
    
    if (buffer.empty()) {
        return -1; // Деструктор lock гарантовано відновить PRIMASK тут!
    }
    
    parse_data(buffer);
    return 0; // Деструктор lock гарантовано відновить PRIMASK тут!
}
