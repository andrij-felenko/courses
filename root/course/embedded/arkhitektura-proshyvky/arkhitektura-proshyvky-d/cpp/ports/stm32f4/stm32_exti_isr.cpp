// ports/stm32f4/stm32_exti_isr.cpp — обробник переривання від кнопки.
// Взірцевий приклад межі: обробник не малює на дисплеї, не пише у флеш і
// нічого не рахує. Він скидає прапорець, кладе подію в чергу й виходить —
// два-три десятки тактів. Уся змістовна робота відбувається згодом, у
// головному циклі, де її не жаль перервати наступним перериванням.
#include "app/events.hpp"
#include "board.hpp"
#include "hal/clock.hpp"
#include "ports/stm32f4/stm32_peripherals.hpp"

namespace {

constexpr std::uint8_t kButtonPin = 0;   // PA0
constexpr hal::Millis  kDebounce{50};

volatile std::uint32_t g_last_click_ms = 0;

} // namespace

extern "C" void EXTI0_IRQHandler()
{
    if ((EXTI->PR & (1U << kButtonPin)) == 0) {
        return;
    }
    EXTI->PR = (1U << kButtonPin);   // прапорець скидається записом одиниці

    const auto now = hal::now();

    // Механічний контакт деренчить кілька мілісекунд і дає десятки
    // переривань на один натиск. Відсіюємо їх найдешевшим способом —
    // порівнянням двох чисел, без таймерів і без затримок в обробнику.
    const auto since_last = static_cast<std::uint32_t>(now.count()) - g_last_click_ms;
    if (since_last < static_cast<std::uint32_t>(kDebounce.count())) {
        return;
    }
    g_last_click_ms = static_cast<std::uint32_t>(now.count());

    app::IEventSink* sink = board::event_sink();
    if (sink == nullptr) {
        return;   // приймач ще не прив'язаний: подію нема куди класти
    }

    // Черга сама бере критичну секцію й сама рахує переповнення, тож
    // навіть коли головний цикл захлинувся, обробник не заклякне.
    static_cast<void>(sink->post(app::SystemEvent{
        .id = app::EventId::ButtonClick,
        .timestamp = now,
        .payload = app::ButtonPayload{.pin = kButtonPin},
    }));
}

namespace port {

void button_exti_init()
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_SYSCFGEN;

    // PA0 — вхід із підтяжкою до живлення, кнопка замикає на землю.
    GPIOA->MODER &= ~(3U << (kButtonPin * 2));
    GPIOA->PUPDR &= ~(3U << (kButtonPin * 2));
    GPIOA->PUPDR |=  (1U << (kButtonPin * 2));

    SYSCFG->EXTICR[0] &= ~SYSCFG_EXTICR1_EXTI0;   // джерело — порт A

    EXTI->IMR  |=  (1U << kButtonPin);   // переривання дозволено
    EXTI->FTSR |=  (1U << kButtonPin);   // спад: натиск
    EXTI->RTSR &= ~(1U << kButtonPin);

    // Пріоритет нижчий за системний таймер: кнопка потерпить, час — ні.
    NVIC_SetPriority(EXTI0_IRQn, 2);
    NVIC_EnableIRQ(EXTI0_IRQn);
}

} // namespace port
