// STM32: задати ПОВІЛЬНУ швидкість наростання на PB5,
// щоб приборкати дзвін на не надто швидкій лінії.
// OSPEEDR: 2 біти на пін; 00 = low speed (найм'якший фронт).
#define OSPEED_LOW   0b00
#define OSPEED_HIGH  0b11

void pin_set_slew_low(GPIO_TypeDef *port, unsigned pin) {
    unsigned shift = pin * 2u;                 // по 2 біти на пін
    port->OSPEEDR &= ~(0b11u << shift);        // очистити поле піна
    port->OSPEEDR |=  ((unsigned)OSPEED_LOW << shift); // 00 = low → плавний фронт
}

// Виклик при ініціалізації плати:
//   pin_set_slew_low(GPIOB, 5);
// Якщо ж лінія справді швидка (SPI на десятки МГц) — там навпаки
// потрібен OSPEED_HIGH, але тоді й термінацію закладай у розведення.
