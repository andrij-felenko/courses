#pragma once

/*
 * Типізований доступ до спеціальних регістрів ядра.
 *
 * Усе, що нижче, — тонкий шар над CMSIS-інтрінсиками; сенс шару в тому, що
 * стан PRIMASK перестає бути «якимось uint32_t», а номер активного
 * переривання повертається як optional<IRQn_Type>, а не як нуль-на-всі-випадки.
 */

#include "stm32f4xx.h"

#include <cstdint>
#include <optional>

namespace cortexm::regs {

enum class CpuMode { Thread, Handler };

enum class PrimaskState : std::uint32_t { Enabled = 0U, Masked = 1U };
enum class FaultmaskState : std::uint32_t { Enabled = 0U, Masked = 1U };

/* ---- Бар'єри ---------------------------------------------------------- */

inline void dsb() noexcept { __DSB(); }
inline void isb() noexcept { __ISB(); }
inline void dmb() noexcept { __DMB(); }

/* Бар'єр самого лише оптимізатора: жодної інструкції не породжує. */
inline void compiler_barrier() noexcept { __ASM volatile ("" ::: "memory"); }

/* ---- PRIMASK ---------------------------------------------------------- */

[[nodiscard]] inline PrimaskState read_primask() noexcept
{
    return static_cast<PrimaskState>(__get_PRIMASK());
}

inline void write_primask(PrimaskState state) noexcept
{
    __set_PRIMASK(static_cast<std::uint32_t>(state));
}

inline void mask_all_irq() noexcept { __disable_irq(); }

/* ---- BASEPRI / FAULTMASK ---------------------------------------------- */

#if !defined(__ARM_ARCH_6M__)

[[nodiscard]] inline std::uint32_t read_basepri() noexcept { return __get_BASEPRI(); }

inline void write_basepri(std::uint32_t raw) noexcept { __set_BASEPRI(raw); }

/* Умовний запис: поріг лише посилюється, ослабити його цим шляхом не можна. */
inline void raise_basepri(std::uint32_t raw) noexcept { __set_BASEPRI_MAX(raw); }

[[nodiscard]] inline FaultmaskState read_faultmask() noexcept
{
    return static_cast<FaultmaskState>(__get_FAULTMASK());
}

inline void write_faultmask(FaultmaskState state) noexcept
{
    __set_FAULTMASK(static_cast<std::uint32_t>(state));
}

inline void mask_all_faults() noexcept { __disable_fault_irq(); }

inline constexpr bool kHasBasepri = true;

#else

inline constexpr bool kHasBasepri = false;   /* ARMv6-M: Cortex-M0/M0+ */

#endif

/* ---- IPSR ------------------------------------------------------------- */

[[nodiscard]] inline CpuMode mode() noexcept
{
    return (__get_IPSR() == 0U) ? CpuMode::Thread : CpuMode::Handler;
}

[[nodiscard]] inline bool in_isr() noexcept { return __get_IPSR() != 0U; }

/*
 * Порожній optional означає «зовнішнього переривання немає»: або Thread Mode,
 * або системне виключення 1..15. Повертати 0 було б брехнею — нуль це
 * справжній номер IRQ0.
 */
[[nodiscard]] inline std::optional<IRQn_Type> active_irq() noexcept
{
    const std::uint32_t ipsr = __get_IPSR();
    if (ipsr < 16U) {
        return std::nullopt;
    }
    return static_cast<IRQn_Type>(ipsr - 16U);
}

}  // namespace cortexm::regs
