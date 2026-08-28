/* CubeMX: PA3 — GPIO_Input (DO), PA5 — GPIO_Output (світло/реле), USART2 — 115200 */
#include "main.h"
#include <stdbool.h>
#include <string.h>

#define DO_PORT   GPIOA
#define DO_PIN    GPIO_PIN_3           // DO давача
#define LED_PORT  GPIOA
#define LED_PIN   GPIO_PIN_5           // світло / реле, яким керуємо

#define DEAF_MS   250u                 // «глухе» вікно після оплеску, мс (гістерезис у часі)

extern UART_HandleTypeDef huart2;

static GPIO_PinState g_idle;           // рівень спокою DO (автовизначення)
static bool     g_wasLoud  = false;    // чи було «гучно» на попередньому оберті (для фронту)
static uint32_t g_lastClap = 0;        // час останнього ЗАРАХОВАНОГО оплеску
static bool     g_lightOn  = false;    // поточний стан світла

static void say(const char *s) {
    HAL_UART_Transmit(&huart2, (uint8_t *)s, strlen(s), HAL_MAX_DELAY);
}

static bool isLoud(void) { return HAL_GPIO_ReadPin(DO_PORT, DO_PIN) != g_idle; }

void clap_setup(void) {                // викликати з main() після MX_GPIO_Init()
    HAL_Delay(50);
    g_idle = HAL_GPIO_ReadPin(DO_PORT, DO_PIN);   // тиша = спокій цієї плати
    say(g_idle == GPIO_PIN_SET ? "Спокій DO = HIGH\r\n" : "Спокій DO = LOW\r\n");
    say("Плесни, щоб перемкнути світло.\r\n");
}

void clap_poll(void) {                 // викликати з while (1) — без жодної затримки
    bool loud = isLoud();

    // Фронт «тихо → гучно»: цього оберту гучно, а минулого було тихо.
    bool rising = loud && !g_wasLoud;
    g_wasLoud = loud;

    // Зараховуємо оплеск, лише якщо минуло «глухе» вікно від попереднього.
    if (rising && (uint32_t)(HAL_GetTick() - g_lastClap) >= DEAF_MS) {
        g_lastClap = HAL_GetTick();
        g_lightOn = !g_lightOn;                    // ПЕРЕКИДАЄМО стан
        HAL_GPIO_WritePin(LED_PORT, LED_PIN, g_lightOn ? GPIO_PIN_SET : GPIO_PIN_RESET);
        say(g_lightOn ? "оплеск → УВІМКНЕНО\r\n" : "оплеск → вимкнено\r\n");
    }
    // інакше це хвіст/відлуння того самого оплеску — мовчки ігноруємо
}
