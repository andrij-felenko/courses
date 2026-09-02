/* Голий супер-цикл: один стек, жодного планувальника.
   Кожен крок неблокуючий рівно настільки, наскільки це дешево, а те, що
   блокує (кадр на SPI), лишається блокуючим — і цикл сам себе на цьому ловить:
   на екран виводиться найбільший фактичний період опитування датчика. */
#include "stm32g0xx.h"

#include "display.h"
#include "sensor.h"

#define SENSOR_PERIOD_MS 100u
#define SCREEN_PERIOD_MS 500u

static volatile uint32_t s_ms;

void SysTick_Handler(void)
{
    s_ms++;
}

/* 32-бітне вирівняне читання на Cortex-M атомарне, тож переривання не глушимо. */
static inline uint32_t millis(void) { return s_ms; }

typedef struct {
    uint32_t gap_max_ms;   /* найбільший фактичний період опитування */
    uint32_t gap_min_ms;
    uint32_t flush_max_ms; /* найдовший кадр на екран                */
} stats_t;

static void watchdog_start(void)
{
    RCC->CSR |= RCC_CSR_LSION;
    while ((RCC->CSR & RCC_CSR_LSIRDY) == 0u) { }

    IWDG->KR  = 0x0000CCCCu; /* запуск                     */
    IWDG->KR  = 0x00005555u; /* дозвіл на запис регістрів  */
    IWDG->PR  = 4u;          /* LSI/64 ≈ 500 Гц            */
    IWDG->RLR = 500u;        /* вікно ≈ 1 с                */
    while (IWDG->SR != 0u) { }
    IWDG->KR = 0x0000AAAAu;
}

static inline void watchdog_kick(void) { IWDG->KR = 0x0000AAAAu; }

static void render(const sensor_t *sensor, const stats_t *st, bool sensor_ok)
{
    display_clear();
    if (sensor_ok) {
        display_number(0u, 0u, sensor_temp_c100(sensor), 2u); /* градуси */
        display_bar(2u, sensor_temp_c100(sensor), -1000, 5000);
    } else {
        display_number(0u, 0u, -1, 0u); /* датчика немає — показуємо це чесно */
    }
    display_number(0u, 4u, (int32_t)st->gap_max_ms, 0u);
    display_number(40u, 4u, (int32_t)st->gap_min_ms, 0u);
    display_number(80u, 4u, (int32_t)st->flush_max_ms, 0u);
    display_number(0u, 6u, (int32_t)sensor->errors, 0u);
}

int main(void)
{
    sensor_t sensor = {0};
    stats_t  st = { 0u, 0xFFFFFFFFu, 0u };
    bool display_ok;
    bool sensor_ok;
    uint32_t next_sensor;
    uint32_t next_screen;
    uint32_t last_sensor_at;

    SystemCoreClockUpdate();
    SysTick_Config(SystemCoreClock / 1000u);

    display_ok = display_init();
    sensor_ok  = sensor_init(&sensor);
    watchdog_start();

    last_sensor_at = millis();
    next_sensor = last_sensor_at;
    next_screen = last_sensor_at + SCREEN_PERIOD_MS;

    for (;;) {
        uint32_t now = millis();

        /* 1. Запуск вимірювання. Порівняння через знак терпить переповнення лічильника. */
        if ((int32_t)(now - next_sensor) >= 0) {
            uint32_t gap = now - last_sensor_at;

            next_sensor += SENSOR_PERIOD_MS;
            if ((int32_t)(now - next_sensor) >= 0) {
                next_sensor = now + SENSOR_PERIOD_MS; /* відстали більше ніж на період */
            }
            last_sensor_at = now;

            if (gap > st.gap_max_ms) { st.gap_max_ms = gap; }
            if ((gap != 0u) && (gap < st.gap_min_ms)) { st.gap_min_ms = gap; }

            sensor_start(&sensor, now);
        }

        /* 2. Крок автомата датчика — не чекає ні на шину, ні на перетворення. */
        if (sensor_poll(&sensor, millis())) {
            sensor_ok = true;
        }

        /* 3. Кадр на екран. Ось вона, блокуюча ділянка на ≈33 мс. */
        if ((int32_t)(now - next_screen) >= 0) {
            uint32_t t0;
            uint32_t took;

            next_screen = now + SCREEN_PERIOD_MS;
            if (display_ok) {
                render(&sensor, &st, sensor_ok);
                t0 = millis();
                display_ok = display_flush();
                took = millis() - t0;
                if (took > st.flush_max_ms) { st.flush_max_ms = took; }
            } else {
                display_ok = display_init(); /* спроба підняти модуль наново */
            }
        }

        /* 4. Сторожовий таймер. Обертів циклу тут тисячі на секунду. */
        watchdog_kick();
    }
}
