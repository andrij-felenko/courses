// services/power_manager.cpp
#include "services/power_manager.hpp"

namespace services {

void PowerManager::on_event(const Event& evt)
{
    if (evt.type != EventType::SensorFault) {
        return;
    }

    if (last_cycle_ && clock_.elapsed_since(*last_cycle_) < min_interval_) {
        // Скидати живлення частіше, ніж давач встигає піднятись, — це не лікування,
        // а самопідтримний цикл відмов.
        ++cycles_suppressed_;
        return;
    }

    last_cycle_ = clock_.now();

    if (!rail_.power_cycle()) {
        ++cycles_failed_;
        return;
    }

    if (!recovery_.reinitialize()) {
        // Живлення повернули, але давач не піднявся. Наступна невдача опитування
        // дасть нову подію несправності — і нову спробу, вже після витримки.
        ++cycles_failed_;
        return;
    }

    ++cycles_done_;
    recovery_.on_recovered();
}

}  // namespace services
