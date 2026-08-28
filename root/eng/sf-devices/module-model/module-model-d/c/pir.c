/* pir.c — той самий взірець, інші деталі всередині */
#define PIR_PIN   GPIO_NUM_5
static const int ACTIVE_LEVEL = 1;     /* PIR active-high: 1 = рух */

void pir_init(void) {
    gpio_set_direction(PIR_PIN, GPIO_MODE_INPUT);   /* без підтяжки: жене сам */
}
bool pir_motion(void) {
    return gpio_get_level(PIR_PIN) == ACTIVE_LEVEL;
}
