// 28BYJ-48 через ULN2003: напівкроковий режим, 8 станів.
// GPIO18,19,21,22 → IN1,IN2,IN3,IN4 (входи каналів 1..4).
// Живлення мотора +5V; його спільний провід — на +5V; ULN2003 стягує фази в −.
#include "driver/gpio.h"
#include "esp_rom_sys.h"        // esp_rom_delay_us(): паузи, коротші за тик FreeRTOS

static const gpio_num_t PHASE[4] = {GPIO_NUM_18, GPIO_NUM_19, GPIO_NUM_21, GPIO_NUM_22};

// Вісім напівкрокових станів. Біт j рядка = рівень на IN(j+1).
static const uint8_t HALFSTEP[8][4] = {
    {1, 0, 0, 0},   // фаза 1
    {1, 1, 0, 0},   // 1+2
    {0, 1, 0, 0},   // 2
    {0, 1, 1, 0},   // 2+3
    {0, 0, 1, 0},   // 3
    {0, 0, 1, 1},   // 3+4
    {0, 0, 0, 1},   // 4
    {1, 0, 0, 1},   // 4+1
};

static void apply_state(int s) {
    for (int j = 0; j < 4; j++)
        gpio_set_level(PHASE[j], HALFSTEP[s][j]);   // виставляємо всі 4 фази цього стану
}

void app_main(void) {
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << GPIO_NUM_18) | (1ULL << GPIO_NUM_19) |
                        (1ULL << GPIO_NUM_21) | (1ULL << GPIO_NUM_22),
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&io);

    while (1) {
        // один повний оберт «уперед»: женемо стани 0→7 багато разів
        for (int i = 0; i < 512; i++) {
            apply_state(i & 7);          // i & 7 циклічно бере 0..7
            esp_rom_delay_us(1500);      // пауза між кроками = швидкість
        }
    }
}
