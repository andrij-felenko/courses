// Дві половини одного вузла: NPN тримає низ, PNP — верх.
static sw_t low_side  = { GPIOB, GPIO_PIN_5, false };  // NPN низом:  «1» → увімк
static sw_t high_side = { GPIOB, GPIO_PIN_6, true  };  // PNP верхом: «0» → увімк

void node_run(void) {
    sw_begin(&low_side);
    sw_begin(&high_side);      // обидва вимкнені (кожен у свій «вимкнено»)

    while (1) {
        // Попри протилежну апаратну полярність, семантика ОДНАКОВА:
        sw_on(&low_side);      // HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, GPIO_PIN_SET)
        sw_on(&high_side);     // HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_RESET)
        HAL_Delay(1000);
        sw_off(&low_side);
        sw_off(&high_side);
        HAL_Delay(1000);
    }
}
