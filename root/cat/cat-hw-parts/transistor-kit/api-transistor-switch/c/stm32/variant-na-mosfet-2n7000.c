// Той самий ключ, той самий тип: для коду MOSFET нічим не відрізняється від NPN низом.
static sw_t mosfet = { GPIOB, GPIO_PIN_5, false };

void mosfet_blink(void) {
    sw_begin(&mosfet);        // затвор у «0», канал закритий
    // Апаратно: затвор → (опц. 100…220 Ом) → вивід; підтяжка 100 кОм затвор→GND.
    // ⚠ вивід STM32 дає 3.3 В — для 2N7000 це мало, див. перевірку нижче.
    while (1) {
        sw_on(&mosfet);  HAL_Delay(500);
        sw_off(&mosfet); HAL_Delay(500);
    }
}
