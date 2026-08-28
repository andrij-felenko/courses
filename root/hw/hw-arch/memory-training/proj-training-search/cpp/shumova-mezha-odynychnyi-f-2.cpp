int find_center_robust(int max_gap)
{
    bool map[RANGE_MAX];
    int n = sweep(map, RANGE_MAX);

    despeckle(map, n, max_gap);            // прибрати шумові провали
    Window w = widest_window(map, n);

    switch (classify(w, n)) {
    case WIN_NONE:
        return -1;                         // канал не заводиться
    case WIN_CLIP_LO:
    case WIN_CLIP_HI:
        report_clip();                     // діагностика: око за межею діапазону
        break;                             // (рішення — далі; тут беремо що є)
    case WIN_OK:
        break;
    }
    return (w.lo + w.hi) / 2;
}
