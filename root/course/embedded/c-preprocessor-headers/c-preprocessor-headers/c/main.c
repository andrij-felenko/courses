#include "led.h"             // свій же заголовок — щоб узгодити оголошення з тілом

void led_init(void) {
    // тут справжня робота з регістрами GPIO
}
void led_on(uint8_t pin) {
    GPIO_OUT_SET = (1u << pin);   // виставити біт піна
}
void led_off(uint8_t pin) {
    GPIO_OUT_CLR = (1u << pin);
}
