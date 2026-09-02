#include "board.h"
#include "debounce.h"
#include "exti_button.h"

/* Обидва підходи зі статті керують тією самою ніжкою PA0, тому в прошивці
   живе рівно один: 0 — періодичне опитування із SysTick, 1 — EXTI з таймером
   блокування. */
#define USE_EXTI_DEBOUNCE 0

static button_t g_button;
static volatile uint32_t g_press_count;

static void on_press(void)
{
    g_press_count++;
    board_led_toggle();
}

void SysTick_Handler(void)
{
    /* Раз на 10 мс. Ніяких HAL_Delay(50) усередині: обробник має піти з ядра
       за одиниці мікросекунд, інакше він з'їсть переривання решти периферії. */
    if (button_update(&g_button, board_button_level()) == BUTTON_EVENT_PRESSED) {
        on_press();
    }
}

int main(void)
{
    board_init();

#if USE_EXTI_DEBOUNCE
    exti_button_init();
#else
    button_init(&g_button, board_button_level());
    board_systick_start_10ms();
#endif

    for (;;) {
#if USE_EXTI_DEBOUNCE
        if (exti_button_take_event() == BUTTON_EVENT_PRESSED) {
            on_press();
        }
#endif
        /* Ядро спить до наступного переривання: у варіанті з опитуванням його
           будить SysTick, у варіанті з EXTI — сама кнопка. */
        __asm volatile ("wfi");
    }
}
