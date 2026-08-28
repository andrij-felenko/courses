#include <math.h>                   // powf(); тіло функції — те саме, що й у вкладці Arduino

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM3_Init();
    build_gamma(2.2f);              // порахувати криву один раз на старті
    leds_init();                    // і лише тоді пускати ШІМ на канали
    while (1) { /* … анімація … */ }
}
