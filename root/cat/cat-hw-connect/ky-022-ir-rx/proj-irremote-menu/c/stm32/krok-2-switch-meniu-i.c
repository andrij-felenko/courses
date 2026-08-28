// Те саме на STM32 HAL: EXTI по спаду + вільний таймер на 1 мкс, NEC розбираємо самі
#include "main.h"
#include <stdio.h>

extern TIM_HandleTypeDef htim2;    // вільний лічильник, 1 тік = 1 мкс
extern TIM_HandleTypeDef htim3;    // ШІМ яскравості, канал 1, період 255

#define IR_PORT   GPIOA
#define IR_PIN    GPIO_PIN_2       // будь-який пін із EXTI, налаштований по спаду
#define MY_REMOTE 0x00             // адреса ТВОГО пульта (знята скелетом)

// коди кнопок ЦЬОГО пульта
enum { BTN_1 = 0x45, BTN_2 = 0x46, BTN_PLAY = 0x40, BTN_UP = 0x15, BTN_DOWN = 0x07 };

static volatile uint16_t rx_addr, rx_cmd;
static volatile uint8_t  rx_ready, rx_repeat;
static uint8_t brightness = 128;   // стан, яким керуємо (0..255)

static void apply_brightness(void) {
    __HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_1, brightness);
    printf("яскравість = %u\r\n", brightness);
}

// увесь розбір NEC — за інтервалами МІЖ СПАДАМИ: 13.5 мс преамбула повного кадру,
// 11.25 мс кадр-повтор, 1.125 мс — біт «0», 2.25 мс — біт «1»
void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    static uint16_t prev; static uint8_t bit; static uint32_t bits;
    if (pin != IR_PIN) return;
    uint16_t now = __HAL_TIM_GET_COUNTER(&htim2);
    uint16_t dt  = now - prev;                  // мкс від попереднього спаду
    prev = now;

    if (dt > 12000 && dt < 15000) { bit = 0; bits = 0; return; }           // повний кадр
    if (dt > 10500 && dt < 12000) { rx_repeat = 1; rx_ready = 1; return; } // кадр-повтор
    if (dt < 900 || dt > 2600) return;                                     // шум
    bits |= (uint32_t)(dt > 1700) << bit;       // молодшим бітом уперед: addr, ~addr, cmd, ~cmd
    if (++bit < 32) return;
    rx_addr   = bits & 0xFF;
    rx_cmd    = (bits >> 16) & 0xFF;
    rx_repeat = 0;
    rx_ready  = 1;
}

int main(void) {
    HAL_Init(); SystemClock_Config();
    MX_GPIO_Init(); MX_TIM2_Init(); MX_TIM3_Init();
    HAL_TIM_Base_Start(&htim2);                 // лічильник мікросекунд для EXTI
    HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);   // ШІМ яскравості
    apply_brightness();

    while (1) {
        if (!rx_ready) continue;
        rx_ready = 0;                    // ← тут аналог resume(): місце під наступний кадр
        if (rx_addr != MY_REMOTE) continue;      // чужий пульт — прапорець уже скинуто

        switch (rx_cmd) {
        case BTN_UP:   if (brightness <= 245) brightness += 10; apply_brightness(); break;
        case BTN_DOWN: if (brightness >= 10)  brightness -= 10; apply_brightness(); break;
        case BTN_PLAY: brightness = brightness ? 0 : 128;       apply_brightness(); break;
        case BTN_1: printf("режим 1\r\n"); break;
        case BTN_2: printf("режим 2\r\n"); break;
        default:    printf("невідома кнопка: 0x%02X\r\n", rx_cmd); break;
        }
    }
}
