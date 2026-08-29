// Критична секція як об'єкт із часом життя.
//
// У C такий блок пишуть парою «підняти BASEPRI … опустити BASEPRI», і кожен
// ранній return між ними — загублене відновлення. Тут вихід із області
// видимості відновлює регістр завжди: і по return, і по break, і по будь-якій
// іншій гілці, яку хтось допише через рік.
#pragma once

#include <cstdint>

#include "cmsis_compiler.h"

namespace isr {

// Маскує переривання ЗІ ЗНАЧЕННЯМ ПРІОРИТЕТУ, БІЛЬШИМ АБО РІВНИМ заданому,
// не чіпаючи вищих. Аварійна лінія, що живе над межею системних викликів,
// крізь цю секцію проходить — у цьому й сенс BASEPRI проти грубого cpsid i.
class BasepriGuard {
public:
    static constexpr std::uint32_t kPriorityBits = 4;

    explicit BasepriGuard(std::uint32_t priority) noexcept
        : saved_{__get_BASEPRI()}
    {
        __set_BASEPRI(priority << (8 - kPriorityBits));
        __DMB();
    }

    ~BasepriGuard() noexcept
    {
        __DMB();
        __set_BASEPRI(saved_);
    }

    BasepriGuard(const BasepriGuard &) = delete;
    BasepriGuard &operator=(const BasepriGuard &) = delete;
    BasepriGuard(BasepriGuard &&) = delete;
    BasepriGuard &operator=(BasepriGuard &&) = delete;

private:
    std::uint32_t saved_;
};

} // namespace isr
