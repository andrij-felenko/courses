#include <stdint.h>

// Поле OSPEEDR: 2 біти на ніжку. Значення: 0=Low, 1=Medium, 2=High, 3=Very High.
#define GPIOA_OSPEEDR (*(volatile uint32_t *)0x40020008u)

void pa5_set_medium_speed(void) {
    uint32_t pin = 5u;
    uint32_t shift = pin * 2u;                 // 2 біти на ніжку → зсув = №×2
    GPIOA_OSPEEDR &= ~(0x3u << shift);         // спершу очистити обидва біти поля
    GPIOA_OSPEEDR |=  (0x1u << shift);         // 0b01 = Medium
}
