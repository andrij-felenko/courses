// bsp_board_rev_a.cpp: Реалізація для ревізії Rev A на C++
#include "bsp_interface.hpp"

namespace bsp {

class Stm32BoardRevA final : public IBoardSupport {
public:
    Status led_set(LedId led, LedState state) noexcept override {
        const auto pin_state = (state == LedState::On) ? GPIO_PIN_SET : GPIO_PIN_RESET;
        switch (led) {
            case LedId::SystemStatus:
                HAL_GPIO_WritePin(GPIOB, GPIO_PIN_12, pin_state);
                return Status::Ok;
            case LedId::Warning:
                HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, pin_state);
                return Status::Ok;
            default:
                return Status::InvalidParam;
        }
    }
    // Інші методи інтерфейсу...
};

} // namespace bsp
