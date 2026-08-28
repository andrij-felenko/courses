#include "cmsis_compiler.h"
#include <cstdint>

namespace embedded::cpu {

enum class CpuMode {
    Thread,  // Головний потік або завдання RTOS
    Handler  // Обробник переривання (ISR)
};

[[nodiscard]] inline CpuMode current_mode() noexcept {
    return (__get_IPSR() == 0U) ? CpuMode::Thread : CpuMode::Handler;
}

[[nodiscard]] inline std::uint32_t get_active_irq_number() noexcept {
    const std::uint32_t ipsr = __get_IPSR();
    return (ipsr >= 16U) ? (ipsr - 16U) : 0U;
}

[[nodiscard]] inline std::uint32_t read_primask() noexcept {
    return __get_PRIMASK();
}

inline void write_primask(std::uint32_t value) noexcept {
    __set_PRIMASK(value);
}

#if (__CORTEX_M >= 3U)
[[nodiscard]] inline std::uint32_t read_basepri() noexcept {
    return __get_BASEPRI();
}

inline void write_basepri(std::uint32_t threshold) noexcept {
    __set_BASEPRI(threshold);
}

inline void write_basepri_max(std::uint32_t threshold) noexcept {
    __set_BASEPRI_MAX(threshold);
}
#endif

} // namespace embedded::cpu
