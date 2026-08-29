#pragma once
/*
 * interrupt_lock.hpp — критична секція як об'єкт із часом життя.
 *
 * Ручна пара «зберегти PRIMASK / відновити PRIMASK» ламається на першому ж
 * ранньому return у гілці помилки: переривання лишаються вимкненими назавжди.
 * Деструктор відновлює стан за будь-якого шляху виходу з області.
 */
#include <cstdint>

#include "cmsis_compiler.h"   /* __get_PRIMASK, __disable_irq, __set_PRIMASK */

namespace nofree {

class InterruptLock {
public:
    InterruptLock() noexcept : primask_{__get_PRIMASK()} { __disable_irq(); }

    /* Відновлюємо саме збережене значення, а не вмикаємо переривання всліпу:
       інакше вкладена секція передчасно розблокувала б зовнішню. */
    ~InterruptLock() noexcept { __set_PRIMASK(primask_); }

    InterruptLock(const InterruptLock &)            = delete;
    InterruptLock &operator=(const InterruptLock &) = delete;

private:
    std::uint32_t primask_;
};

/* Використання:
 *
 *   {
 *       nofree::InterruptLock lock;      // переривання вимкнені
 *       session = pool.make();           // безпечна робота зі списком вільних
 *   }                                    // стан PRIMASK повернувся сам
 */

}  // namespace nofree
