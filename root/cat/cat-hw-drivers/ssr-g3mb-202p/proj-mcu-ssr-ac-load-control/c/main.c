#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "g3mb202p.h"

/* Вивід GPIO мікроконтролера, підключений до входу твердотільного реле G3MB-202P */
#define RELAY_GPIO_PIN 5

/* Симульований лічильник системних мілісекунд (millis) */
static uint32_t g_simulated_millis = 0;

/**
 * @brief Симуляція апаратного виклику запису в GPIO вивід мікроконтролера.
 * 
 * @param pin Номер GPIO виводу.
 * @param level Логічний рівень (true = HIGH, false = LOW).
 */
static void platform_gpio_write(uint8_t pin, bool level)
{
    printf("[HW GPIO] Вивід GPIO_%u -> %s (%s)\n",
           pin,
           level ? "HIGH (1)" : "LOW (0)",
           level ? "Світлодіод оптичного входу заживлено" : "Світлодіод оптичного входу знеструмлено");
}

/**
 * @brief Симуляція апаратної затримки МК у мілісекундах із нарощуванням системного часового штампу.
 * 
 * @param ms Тривалість затримки в мілісекундах.
 */
static void platform_delay_ms(uint32_t ms)
{
    printf("   [Таймер] Затримка %u мс...\n", (unsigned int)ms);
    g_simulated_millis += ms;
}

/**
 * @brief Симуляція системного таймера мікроконтролера (аналог millis() в Arduino або HAL_GetTick()).
 * 
 * @return Системний час у мілісекундах.
 */
static uint32_t platform_get_ms(void)
{
    return g_simulated_millis;
}

/**
 * @brief Допоміжна функція виводу поточного фіксованого стану драйвера.
 * 
 * @param driver Вказівник на дескриптор реле.
 */
static void print_relay_status(const g3mb202p_t *driver)
{
    g3mb202p_state_t state;
    if (g3mb202p_get_state(driver, &state) == G3MB202P_OK) {
        printf(" -> Поточний зафіксований стан реле: %s\n",
               (state == G3MB202P_STATE_ON) ? "УВІМКНЕНО (ON)" : "ВИМКНЕНО (OFF)");
    }
}

int main(void)
{
    printf("=== Драйвер твердотільного реле G3MB-202P (2 A / 240 V AC) ===\n\n");

    /*
     * Принцип роботи G3MB-202P:
     * - Твердотільне реле (SSR) оптично розв'язане від мікроконтролера.
     * - Містить вбудовану схему переходу через нуль (Zero-Crossing Circuit).
     * - При поданні вхідного керуючого сигналу увімкнення симістор відкривається
     *   не негайно, а при найближчому переході напруги мережі 240 В через 0 В (затримка до ~10 мс при 50 Гц).
     * - Це мінімізує пускові струми, усуває високочастотні електромагнітні завади (EMI)
     *   і захищає контактні групи та комутовані прилади змінного струму.
     */

    /* 1. Конфігурація драйвера G3MB-202P */
    g3mb202p_config_t config = {
        .gpio_pin = RELAY_GPIO_PIN,
        .active_level = G3MB202P_ACTIVE_HIGH, /* Active HIGH: логічна 1 вмикає світлодіод */
        .initial_state = G3MB202P_STATE_OFF,  /* Початковий безпечний стан: вимкнено */
        .min_switch_interval_ms = 200,        /* Захисний інтервал від надчастої комутації */
        .gpio_write = platform_gpio_write,
        .delay_ms = platform_delay_ms,
        .get_ms = platform_get_ms
    };

    g3mb202p_t ssr_driver;

    /* 2. Ініціалізація модуля драйвера */
    printf("1. Безпечна ініціалізація драйвера G3MB-202P...\n");
    g3mb202p_status_t status = g3mb202p_init(&ssr_driver, &config);
    if (status != G3MB202P_OK) {
        printf("Помилка ініціалізації драйвера (код %d)!\n", status);
        return 1;
    }
    printf("Драйвер успішно ініціалізовано.\n");
    print_relay_status(&ssr_driver);
    printf("\n");

    /* 3. Безпечне увімкнення силового навантаження */
    printf("2. Запит увімкнення навантаження 240 В (g3mb202p_turn_on):\n");
    status = g3mb202p_turn_on(&ssr_driver);
    if (status == G3MB202P_OK) {
        print_relay_status(&ssr_driver);
        printf("   [Примітка] Силовий триак відкриється в момент переходу напруги AC через 0 V.\n");
    }
    printf("\n");

    /* 4. Перевірка захисту від надчастотного перемикання (Throttling) */
    printf("3. Спроба негайного повторного перемикання (без витримки паузи 200 мс):\n");
    status = g3mb202p_turn_off(&ssr_driver);
    if (status == G3MB202P_ERROR_THROTTLED) {
        printf("   [Захист] Запит відхилено: часовий інтервал комутації ще не минув (Throttled).\n");
        print_relay_status(&ssr_driver);
    }
    printf("\n");

    /* 5. Витримка необхідного інтервалу затримки */
    printf("4. Витримка часового інтервалу 250 мс...\n");
    platform_delay_ms(250);
    printf("\n");

    /* 6. Безпечне вимкнення навантаження після витримки паузи */
    printf("5. Повторна спроба вимкнення навантаження 240 В (g3mb202p_turn_off):\n");
    status = g3mb202p_turn_off(&ssr_driver);
    if (status == G3MB202P_OK) {
        print_relay_status(&ssr_driver);
        printf("   [Примітка] Струм триака перерветься при переході струму AC через нуль.\n");
    }
    printf("\n");

    /* 7. Періодичне перемикання стану (Toggle) */
    printf("6. Безпечне інвертування стану (g3mb202p_toggle):\n");
    platform_delay_ms(250);
    status = g3mb202p_toggle(&ssr_driver);
    if (status == G3MB202P_OK) {
        print_relay_status(&ssr_driver);
    }
    printf("\n");

    printf("7. Завершальне вимкнення силового навантаження:\n");
    platform_delay_ms(250);
    g3mb202p_turn_off(&ssr_driver);
    print_relay_status(&ssr_driver);

    printf("\n=== Демонстрацію роботи драйвера G3MB-202P успішно завершено ===\n");
    return 0;
}
