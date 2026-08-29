// main.cpp — точка входу цільової прошивки: тут і тільки тут переносна
// логіка знайомиться з конкретною платою.
#include "stm32_board.hpp"
#include "supervisor.hpp"

#include "stm32f4xx_hal.h"

extern "C" {
void SystemClock_Config(void);
void MX_GPIO_Init(void);
void MX_ADC1_Init(void);
void MX_I2C1_Init(void);
void MX_RTC_Init(void);
}

namespace {

// Плата не піднялася: блимаємо аварійним світлодіодом до перезавантаження
// сторожовим таймером.
[[noreturn]] void fatal_blink()
{
    for (;;) {
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_4);
        HAL_Delay(200);
    }
}

} // namespace

int main()
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_ADC1_Init();
    MX_I2C1_Init();
    MX_RTC_Init();

    // Об'єкт плати живе весь час роботи прошивки — статичне сховище,
    // жодної купи в системі без динамічної пам'яті.
    static bsp::Stm32Board board;
    if (board.init() != bsp::Status::Ok) {
        fatal_blink();
    }

    // Ось і все впровадження залежності: посилання на реалізацію.
    app::SystemSupervisor supervisor(board);

    for (;;) {
        supervisor.run_cycle();

        // Після критичного розряду супервізор уже відспав годину.
        if (!supervisor.is_critical_shutdown()) {
            board.enter_low_power(bsp::SleepMode::Light, app::kCyclePeriod);
        }
    }
}
