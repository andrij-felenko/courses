static sw_t pump = { GPIOB, GPIO_PIN_5, false };  // NPN низом: «1» вмикає
static sw_t lamp = { GPIOB, GPIO_PIN_6, true  };  // PNP верхом: «0» вмикає

int main(void) {
    HAL_Init();
    SystemClock_Config();     // згенерований CubeMX-ом розгін тактування
    sw_begin(&pump);
    sw_begin(&lamp);          // обидва стартують ВИМКНЕНИМИ

    while (1) {
        sw_on(&pump);         // «увімкнути насос» — байдуже, що там NPN
        HAL_Delay(3000);
        sw_off(&pump);
        sw_toggle(&lamp);     // перемкнути лампу в протилежний стан
        HAL_Delay(1000);
    }
}
