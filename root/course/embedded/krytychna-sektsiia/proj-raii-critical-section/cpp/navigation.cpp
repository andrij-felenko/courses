/*
 * Прошивкова обв'язка навігації: конкретна політика блокування, єдиний
 * екземпляр менеджера й перехідник із векторної таблиці.
 *
 * Цю одиницю трансляції складають лише під ціль (PrimaskLockPolicy існує
 * тільки для ARM); саме з неї знято асемблерний лістинг asm/navigation_update.s.
 */

#include "navigation.hpp"

namespace flight {
namespace {

using Navigation = NavigationManager<embedded::sync::PrimaskLockPolicy>;

Navigation g_navigation;

}  // namespace

void telemetry_step() noexcept
{
    if (const auto fix = g_navigation.snapshot()) {
        radio_send(*fix);   // передача — ПОЗА критичною секцією
    }
}

/* Тіло обробника переривання GNSS. */
void on_gnss_irq() noexcept
{
    NavigationData fix;
    if (gnss_read_fix(fix)) {   // битий кадр лишає старий фікс чинним
        g_navigation.update(fix);
    }
}

}  // namespace flight

/* Символ, який стоїть у векторній таблиці: C++ імена там не працюють. */
extern "C" void GNSS_IRQHandler(void)
{
    flight::on_gnss_irq();
}
