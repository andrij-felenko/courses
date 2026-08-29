// safety.hpp — детермінований аварійний стан виконавчих органів.
//
// Безпечний стан — це не «зупинити керування», а фізично знеструмити те,
// що може рухатися, нагрівати чи вмикати напругу. Він мусить наставати
// і при аварії прошивки, і на кожному старті — до того, як почне
// виконуватися хоч один рядок прикладної логіки.
#pragma once

#include "crash_report.hpp"

namespace safety {

// Силовий каскад: міст на TIM1 плюс лінія дозволу драйвера й реле
// відсікання. Стан у системі рівно один, тому це фасад, а не об'єкт.
class PowerStage {
public:
    PowerStage() = delete;

    // Перше, що робить прошивка після скидання: переводить лінії керування
    // силовими ключами у вихід із рівнем «вимкнено». До цього виклику вони
    // лишаються входами, і зовнішні підтяжки на платі тримають драйвери
    // закритими — саме тому підтяжки в серійному виробі обов'язкові.
    static void arm_outputs() noexcept;

    // Повертає false, якщо систему вже зафіксовано в аварійному стані.
    [[nodiscard]] static bool enable() noexcept;

    // Штатне вимкнення каскаду: сеанс керування скінчився. Аварії не
    // оголошує, фіксації не ставить — на відміну від shutdown().
    static void release() noexcept;

    // Аварійне знеструмлення з фіксацією. Ідемпотентне, придатне до виклику
    // з обробника винятку й із вимкненими перериваннями.
    static void shutdown() noexcept;

    [[nodiscard]] static bool energised() noexcept;

    // true, якщо знеструмлення сталося через аварію й тримається до рестарту.
    [[nodiscard]] static bool latched() noexcept;
};

// Дозвіл на роботу силової частини як час життя об'єкта. У C ту саму
// гарантію тримають вручну: кожна гілка виходу мусить не забути про
// goto out. Тут вихід з області видимості — байдуже, звичайний чи
// через раннє повернення — гасить каскад сам.
class PowerStageGuard {
public:
    // permitted == false означає «дозволу немає»: каскад навіть не
    // пробують заводити. Прапорець проходить через конструктор, а не
    // через if навколо нього, щоб об'єкт існував у будь-якому разі
    // і код нижче мав однакову форму.
    explicit PowerStageGuard(bool permitted = true) noexcept;
    ~PowerStageGuard() noexcept;

    PowerStageGuard(const PowerStageGuard&) = delete;
    PowerStageGuard& operator=(const PowerStageGuard&) = delete;
    PowerStageGuard(PowerStageGuard&&) = delete;
    PowerStageGuard& operator=(PowerStageGuard&&) = delete;

    [[nodiscard]] explicit operator bool() const noexcept { return armed_; }

private:
    bool armed_;
};

// Монітор живлення. Апаратний BOR виставляється ф'юзами й тримає ядро
// в скиданні нижче свого порога; PVD — другий, програмний рубіж ВИЩЕ
// за BOR: він дає кількасот мікросекунд, щоб добровільно погасити силову
// частину й не почати запис у Flash перед самою смертю живлення.
class SupplyMonitor {
public:
    SupplyMonitor() = delete;

    static void init() noexcept;
    [[nodiscard]] static bool sagging() noexcept;
};

// Аварійне завершення роботи. Порядок дій усередині не обговорюється:
// спершу знеструмити, потім записати, і лише потім перезапускати.
[[noreturn]] void panic(diag::PanicReason reason) noexcept;
[[noreturn]] void panic(diag::PanicReason reason, const diag::FaultContext& context) noexcept;

// Перевірка інваріанта, яку не вимикають у релізі: у виробі краще
// керований рестарт із діагностикою, ніж мовчазна робота на сміттєвих даних.
inline void require(bool condition,
                    diag::PanicReason reason = diag::PanicReason::assertion) noexcept
{
    if (!condition) [[unlikely]] {
        panic(reason);
    }
}

} // namespace safety
