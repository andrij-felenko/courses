// Людські імена гіпотез під конкретний список (паралельно suspect_t).
// Тут — по імені кожного вузла; можна давати й змістовніші формулювання.
static const char *SUS_NAME[SUS_COUNT] = {
    "зайвий фільтр", "шлях DMA", "радіо", "зовн. давач",
    "годування сторожа", "енергозбереження", "скид журналу", "перевірка OTA"
};

// Повна бісекція: половинний пошук + журнал досліду на кожному кроці.
// n — скільки підозрюваних (2..32); repro — предикат. Повертає індекс винуватця.
int bisect_debug(int n, predicate_fn repro) {
    int lo = 0, hi = n - 1, step = 0;

    JOURNAL_NOTE("=== бісекція старт: перевіряю, що весь список дає збій ===");
    suspects_set_mask(mask_range(lo, hi));       // ввімкнути ВСІХ
    settle_and_run();
    if (!repro()) {
        // Весь список — і збою нема. Винного в списку немає, бісекція неможлива.
        JOURNAL_NOTE("увесь список чистий: винуватця в списку НЕМА (або предикат бреше)");
        return -1;
    }

    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        uint32_t m = mask_range(lo, mid);        // вмикаємо нижню половину вікна

        suspects_set_mask(m);
        settle_and_run();
        int verdict = repro();

        JOURNAL(++step,
                SUS_NAME[mid],                    // гіпотеза: межа розрізу — на цьому вузлі
                m, popcount_mask(m), verdict);

        if (verdict) hi = mid;                    // збій лишився → винуватець у [lo..mid]
        else         lo = mid + 1;                // збій зник     → він у [mid+1..hi]
    }

    JOURNAL(++step, SUS_NAME[lo], (1u << (uint32_t)lo), 1, 1);
    JOURNAL_NOTE("=== ВИНУВАТЕЦЬ ЛОКАЛІЗОВАНИЙ ===");
    return lo;
}
