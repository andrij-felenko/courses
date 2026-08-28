// Пробник для монотонного випадку: true, якщо за коду затримки
// чіп повернув рівень CK == 1 (строб уже наздогнав фронт).
bool probe_ck_is_high(int code)
{
    knob_set(code);
    settle();
    return probe_once();     // тут probe_once читає біт, повернений чіпом на DQ
}

// Бінарний пошук першого коду, за якого відповідь стала 1
// (перехід 0 -> 1) на монотонній осі 0 .. range_max-1.
// Повертає цей код, або range_max, якщо 1 не з'явилась узагалі.
int find_transition(int range_max)
{
    int lo = 0, hi = range_max;           // шукаємо в [lo, hi): перший code з '1'
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;     // так безпечніше від переповнення
        if (probe_ck_is_high(mid))
            hi = mid;                      // '1' тут — межа не правіше mid
        else
            lo = mid + 1;                  // '0' тут — межа строго правіше
    }
    return lo;                             // перший код з '1'; == range_max, якщо '1' нема
}
