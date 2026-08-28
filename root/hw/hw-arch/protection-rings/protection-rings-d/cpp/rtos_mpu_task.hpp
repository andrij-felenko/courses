// rtos_mpu_task.hpp / .cpp — ідіоматичний C++20 драйвер MPU та перемикача контексту
// Платформа: ARM Cortex-M4 / Cortex-M7 (ARMv7-M, GCC/Clang -std=c++20)
#pragma once
#include <cstdint>
#include <span>
#include <concepts>

namespace rtos::hal {

enum class AccessPermission : uint32_t {
    NoAccess           = 0b000UL << 24,
    PrivilegedRwOnly   = 0b001UL << 24,
    PrivilegedRwUserRo = 0b010UL << 24,
    FullAccessRw       = 0b011UL << 24,
    PrivilegedRoUserRo = 0b110UL << 24
};

enum class RegionSize : uint32_t {
    Size32B   = 4UL  << 1,
    Size1KB   = 9UL  << 1,
    Size4KB   = 11UL << 1,
    Size512KB = 18UL << 1
};

struct MpuHardwareRegisters {
    volatile uint32_t TYPE;
    volatile uint32_t CTRL;
    volatile uint32_t RNR;
    volatile uint32_t RBAR;
    volatile uint32_t RASR;
};

struct ScbHardwareRegisters {
    volatile uint32_t CPUID;
    volatile uint32_t ICSR;
    volatile uint32_t VTOR;
    volatile uint32_t AIRCR;
    volatile uint32_t SCR;
    volatile uint32_t CCR;
    volatile uint32_t SHPR[3];
    volatile uint32_t SHCSR;
    volatile uint32_t CFSR;
};

inline auto* const MPU = reinterpret_cast<MpuHardwareRegisters*>(0xE000ED90UL);
inline auto* const SCB = reinterpret_cast<ScbHardwareRegisters*>(0xE000ED00UL);

class MemoryProtectionUnit {
public:
    static void init() noexcept {
        __asm__ volatile ("dsb 0xF" ::: "memory");
        SCB->SHCSR |= (1UL << 16); // Увімкнення MemManage Fault
        MPU->CTRL = 0;             // Скидання перед конфігурацією
    }

    static void configure_region(uint8_t region_num,
                                 uintptr_t base_address,
                                 RegionSize size,
                                 AccessPermission perm,
                                 bool execute_never = true) noexcept {
        MPU->RNR  = region_num;
        MPU->RBAR = base_address;
        
        uint32_t rasr = 1UL // Enable
                      | static_cast<uint32_t>(size)
                      | static_cast<uint32_t>(perm)
                      | (execute_never ? (1UL << 28) : 0UL);
        MPU->RASR = rasr;
    }

    static void enable() noexcept {
        // Біт 0 = ENABLE, біт 2 = PRIVDEFENA (фонова пам'ять для ядра)
        MPU->CTRL = (1UL << 0) | (1UL << 2);
        __asm__ volatile ("dsb 0xF \n isb 0xF" ::: "memory");
    }
};

class TaskLauncher {
public:
    template <typename TaskFn>
    requires std::invocable<TaskFn>
    [[noreturn]] static void launch_unprivileged(TaskFn&& task_entry, uintptr_t psp_stack_top) noexcept {
        __asm__ volatile ("msr psp, %0" :: "r"(psp_stack_top) : "sp");

        // Біт 1 = SPSEL (PSP), Біт 0 = nPRIV (Unprivileged)
        constexpr uint32_t unprivileged_control = 0b11UL;
        __asm__ volatile (
            "msr control, %0 \n"
            "isb             \n"
            :: "r"(unprivileged_control) : "memory"
        );

        task_entry();
        while (true) { /* У разі повернення — зупинка */ }
    }
};

} // namespace rtos::hal
