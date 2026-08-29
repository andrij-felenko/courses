// Прошивка стенда: серія з 256 оптичних спалахів, вимір інтервалу «спалах ->
// поява плями на екрані», зведення по вибірці у послідовний порт.
#include <stdbool.h>
#include <stdint.h>

#include "hw.h"
#include "rig.h"
#include "stats.h"

#define TRIALS               256u
#define COOLDOWN_MIN_US   80000u  // 80 мс
#define COOLDOWN_SPAN_US  80000u  // + [0; 80) мс -> вікно 80..160 мс
#define TIMEOUT_GIVE_UP      16u  // стільки поспіль втрачених кадрів = тракт мертвий

// Xorshift32: два зсуви й xor, жодних ділень і жодної таблиці. Для розведення
// спалахів по фазі кадрової розгортки цієї якості випадковості досить.
static uint32_t rnd_state = 0x2545F491u;

static uint32_t rnd_next(void)
{
    uint32_t x = rnd_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rnd_state = x;
    return x;
}

// Пауза між випробуваннями — випадкова. Фіксована пауза рано чи пізно ляже в
// резонанс із кадровою розгорткою камери, і всі 256 спалахів потраплять в одну
// й ту саму фазу кадру: вибірка вийде красива й брехлива.
static uint32_t cooldown_us(void)
{
    return COOLDOWN_MIN_US + (rnd_next() % COOLDOWN_SPAN_US);
}

// Виконує одне випробування до кінця. Друкувати всередині вікна не можна:
// один символ на 115200 бод — це 87 мкс блокувального очікування, і вони
// лягли б просто у виміряний інтервал.
static rig_result_t run_trial(void)
{
    while (!rig_trigger()) {
        rig_arm(); // автомат ще в охолодженні після попереднього спалаху
    }

    rig_result_t result;
    do {
        result = rig_poll();
    } while (!result.completed);

    return result;
}

static void print_trial(uint16_t index, rig_result_t result)
{
    hw_print("#");
    hw_print_u32(index + 1u);
    if (result.timed_out) {
        hw_print("  ВТРАЧЕНО КАДР\n");
    } else {
        hw_print("  ");
        hw_print_ms(result.latency_us);
        hw_print(" мс\n");
    }
}

static void print_summary(const stats_summary_t *sum)
{
    hw_print("\n--- Бюджет затримки тракту ---\n");
    hw_print("Вимірів:   ");
    hw_print_u32(sum->count);
    hw_print(" з ");
    hw_print_u32(TRIALS);
    hw_print_nl();

    hw_print("Втрачено:  ");
    hw_print_u32(sum->timeouts);
    hw_print_nl();

    if (sum->count == 0u) {
        hw_print("Жодного відгуку. Перевірте поріг компаратора, засвітку\n"
                 "фотодіода та наявність картинки на екрані.\n");
        return;
    }

    hw_print("Мінімум:   "); hw_print_ms(sum->min_us);    hw_print(" мс\n");
    hw_print("Медіана:   "); hw_print_ms(sum->p50_us);    hw_print(" мс\n");
    hw_print("Середнє:   "); hw_print_ms(sum->mean_us);   hw_print(" мс\n");
    hw_print("P95:       "); hw_print_ms(sum->p95_us);    hw_print(" мс\n");
    hw_print("P99:       "); hw_print_ms(sum->p99_us);    hw_print(" мс\n");
    hw_print("Максимум:  "); hw_print_ms(sum->max_us);    hw_print(" мс\n");
    hw_print("Джитер:    "); hw_print_ms(sum->jitter_us); hw_print(" мс\n");

    // Втрати самі по собі затримки не міряють, але без них зведення бреше:
    // тракт, що загубив кожен десятий кадр, має чудову медіану й непридатне
    // керування.
    if (sum->timeouts * 10u > (sum->count + sum->timeouts)) {
        hw_print("УВАГА: втрачено понад 10% кадрів — зведення не характеризує тракт.\n");
    }
}

int main(void)
{
    hw_init();
    rig_init();

    stats_t stats;
    stats_init(&stats);

    hw_print("\nСтенд вимірювання затримки: серія з ");
    hw_print_u32(TRIALS);
    hw_print(" спалахів\n");

    // Зерно беремо з часової бази: між подачею живлення й першим спалахом
    // завжди лежить різна кількість мікросекунд.
    rnd_state ^= hw_now_us() | 1u;

    uint16_t timeout_streak = 0u;

    for (uint16_t i = 0u; i < TRIALS; ++i) {
        const rig_result_t result = run_trial();

        if (result.timed_out) {
            stats_add_timeout(&stats);
            timeout_streak++;
        } else {
            stats_add(&stats, result.latency_us);
            timeout_streak = 0u;
        }

        print_trial(i, result);

        if (timeout_streak >= TIMEOUT_GIVE_UP) {
            hw_print("\nПоспіль втрачено ");
            hw_print_u32(timeout_streak);
            hw_print(" кадрів — серію обірвано.\n");
            break;
        }

        hw_delay_us(cooldown_us());
        rig_arm();
    }

    stats_summary_t summary;
    stats_summarize(&stats, &summary);
    print_summary(&summary);

    // Прошивка стенда нікуди не повертається: результат має лишитися на екрані
    // термінала, а світлодіод — погашеним.
    hw_led(false);
    for (;;) {
        __asm volatile("wfi");
    }
}
