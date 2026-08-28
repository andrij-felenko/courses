#define OUT_PORT     GPIOC
#define OUT_PIN      GPIO_PIN_13        // те, чим керуємо (світлодіод/реле)
#define CLAP_WINDOW  300                // придушення торохтіння одного оплеску
#define DOUBLE_GAP   600                // максимум між двома оплесками пари

void clap_switch_poll(void) {           // кличемо щоразу з головного while (1)
    static uint8_t was_sound = 0, clap_count = 0;
    static GPIO_PinState out_state = GPIO_PIN_RESET;
    static uint32_t last_clap = 0;

    uint8_t is_sound = (HAL_GPIO_ReadPin(DO_PORT, DO_PIN) != idle_level);
    uint32_t now = HAL_GetTick();

    if (is_sound && !was_sound && now - last_clap > CLAP_WINDOW) {
        // зарахований новий оплеск
        if (now - last_clap < DOUBLE_GAP) clap_count++;   // близько до попереднього — пара
        else                              clap_count = 1; // задалеко — лічба спершу
        last_clap = now;

        if (clap_count >= 2) {          // два оплески поспіль — перемикаємось
            out_state = (out_state == GPIO_PIN_SET) ? GPIO_PIN_RESET : GPIO_PIN_SET;
            HAL_GPIO_WritePin(OUT_PORT, OUT_PIN, out_state);
            clap_count = 0;             // щоб потрійний не порахувався ще раз
            printf(out_state == GPIO_PIN_SET ? "УВІМК\r\n" : "ВИМК\r\n");
        }
    }
    was_sound = is_sound;
}
