#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/hrtimer.h>
#include <linux/ktime.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix-Linux Reference");
MODULE_DESCRIPTION("High-Resolution Timer Kernel Module Example");

static struct hrtimer my_hrtimer;
static ktime_t period_ns;
static u64 fire_count = 0;

static enum hrtimer_restart hrtimer_callback(struct hrtimer *timer) {
    ktime_t now = ktime_get();
    fire_count++;

    /* Оновлюємо час наступного спрацьовування, уникаючи накопичення похибки */
    hrtimer_forward(timer, now, period_ns);

    if (fire_count % 4000 == 0) {
        pr_info("hrtimer_example: 4000 спрацьовувань зафіксовано\n");
    }

    /* Вказуємо підсистемі перезапустити таймер у дереві */
    return HRTIMER_RESTART;
}

static int __init hrtimer_example_init(void) {
    /* 250 мікросекунд = 250 000 наносекунд */
    period_ns = ktime_set(0, 250000);

    /* Ініціалізуємо hrtimer для монотонного годинника у відносному режимі.
       hrtimer_setup() доступний з ядра 6.14 і від 6.15 є єдиним способом:
       давню пару hrtimer_init(&my_hrtimer, CLOCK_MONOTONIC, HRTIMER_MODE_REL)
       з окремим присвоєнням my_hrtimer.function = hrtimer_callback у 6.15 прибрано. */
    hrtimer_setup(&my_hrtimer, hrtimer_callback, CLOCK_MONOTONIC, HRTIMER_MODE_REL);

    pr_info("hrtimer_example: запуск hrtimer з періодом 250 мкс\n");
    hrtimer_start(&my_hrtimer, period_ns, HRTIMER_MODE_REL);

    return 0;
}

static void __exit hrtimer_example_exit(void) {
    int ret = hrtimer_cancel(&my_hrtimer);
    if (ret) {
        pr_info("hrtimer_example: активний таймер скасовано при вивантаженні\n");
    }
    pr_info("hrtimer_example: модуль вивантажено, всього спрацьовувань: %llu\n", fire_count);
}

module_init(hrtimer_example_init);
module_exit(hrtimer_example_exit);
