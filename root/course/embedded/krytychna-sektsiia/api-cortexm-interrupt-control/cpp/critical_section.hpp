#pragma once

/*
 * Критична секція як час життя об'єкта.
 *
 * У C секцію закривають парним викликом exit — і кожен ранній return чи
 * goto є шансом його загубити. Тут маску знімає деструктор, тому вихід із
 * області видимості будь-яким шляхом закриває секцію рівно один раз і
 * відновлює саме той стан, що був до входу.
 */

#include "cortexm_regs.hpp"
#include "nvic_priority.hpp"

#include <utility>

namespace cortexm {

/* Глобальна секція: не працює ніхто, крім NMI та HardFault. */
class PrimaskGuard {
public:
    PrimaskGuard() noexcept : saved_{regs::read_primask()}
    {
        regs::mask_all_irq();
        regs::compiler_barrier();
    }

    ~PrimaskGuard() noexcept
    {
        regs::compiler_barrier();
        regs::dsb();                  /* записи секції — у пам'ять */
        regs::write_primask(saved_);  /* відновлення, а не безумовне вмикання */
        regs::isb();
    }

    PrimaskGuard(const PrimaskGuard&) = delete;
    PrimaskGuard& operator=(const PrimaskGuard&) = delete;
    PrimaskGuard(PrimaskGuard&&) = delete;
    PrimaskGuard& operator=(PrimaskGuard&&) = delete;

private:
    regs::PrimaskState saved_;
};

#if !defined(__ARM_ARCH_6M__)

/* Секція за порогом: усе, що терміновіше за поріг, працює далі. */
class BasepriGuard {
public:
    explicit BasepriGuard(Basepri threshold) noexcept : saved_{regs::read_basepri()}
    {
        regs::raise_basepri(threshold.raw());   /* вкладеність лише посилює */
        regs::compiler_barrier();
    }

    ~BasepriGuard() noexcept
    {
        regs::compiler_barrier();
        regs::dsb();
        regs::write_basepri(saved_);
        regs::isb();
    }

    BasepriGuard(const BasepriGuard&) = delete;
    BasepriGuard& operator=(const BasepriGuard&) = delete;
    BasepriGuard(BasepriGuard&&) = delete;
    BasepriGuard& operator=(BasepriGuard&&) = delete;

private:
    std::uint32_t saved_;
};

/* Найгостріша секція: блокує навіть HardFault. Помилка всередині = Lockup. */
class FaultmaskGuard {
public:
    FaultmaskGuard() noexcept : saved_{regs::read_faultmask()}
    {
        regs::mask_all_faults();
        regs::compiler_barrier();
    }

    ~FaultmaskGuard() noexcept
    {
        regs::compiler_barrier();
        regs::dsb();
        regs::write_faultmask(saved_);
        regs::isb();
    }

    FaultmaskGuard(const FaultmaskGuard&) = delete;
    FaultmaskGuard& operator=(const FaultmaskGuard&) = delete;

private:
    regs::FaultmaskState saved_;
};

#else

/* На ARMv6-M порогу немає: тип лишається, а секція виходить глобальна. */
class BasepriGuard {
public:
    explicit BasepriGuard(Basepri) noexcept {}

    BasepriGuard(const BasepriGuard&) = delete;
    BasepriGuard& operator=(const BasepriGuard&) = delete;

private:
    PrimaskGuard global_{};
};

#endif

/* Секція навколо виразу: результат лямбди повертається назовні як є. */
template <typename Fn>
decltype(auto) with_irq_masked(Fn&& fn)
{
    PrimaskGuard guard;
    return std::forward<Fn>(fn)();
}

template <typename Fn>
decltype(auto) with_priority_masked(Basepri threshold, Fn&& fn)
{
    BasepriGuard guard{threshold};
    return std::forward<Fn>(fn)();
}

/*
 * Спільна змінна, більша за машинне слово.
 *
 * Поріг задається один раз, разом зі змінною, — і далі жоден виклик не може
 * прочитати її «просто так», забувши секцію. Письменник із перериванням того
 * самого пріоритету бере посилання через from_isr(): він і так не витісняється
 * ані фоном, ані собі рівним.
 */
template <typename T>
class Shared {
public:
    constexpr explicit Shared(Basepri lock, T initial = T{}) noexcept
        : lock_{lock}, value_{initial}
    {
    }

    [[nodiscard]] T load() const noexcept
    {
        BasepriGuard guard{lock_};
        return value_;
    }

    void store(const T& next) noexcept
    {
        BasepriGuard guard{lock_};
        value_ = next;
    }

    /* Читання-зміна-запис однією секцією замість двох. */
    template <typename Fn>
    decltype(auto) modify(Fn&& fn)
    {
        BasepriGuard guard{lock_};
        return std::forward<Fn>(fn)(value_);
    }

    [[nodiscard]] T& from_isr() noexcept { return value_; }

private:
    Basepri lock_;
    T value_;
};

}  // namespace cortexm
