struct Window {
    int lo;        // індекс першої P у вікні
    int hi;        // індекс останньої P у вікні
    int width;     // hi - lo + 1; 0 = вікна нема (усе F)
};

// Знаходить НАЙШИРШЕ суцільне вікно P у map[0..n-1].
Window widest_window(const bool map[], int n)
{
    Window best = { -1, -1, 0 };
    int cur_lo = -1;                       // початок поточної смуги, -1 = поза смугою

    for (int i = 0; i < n; i++) {
        if (map[i]) {
            if (cur_lo < 0) cur_lo = i;    // смуга щойно почалась
            int w = i - cur_lo + 1;
            if (w > best.width) {          // поточна побила рекорд — зберігаємо
                best.lo = cur_lo;
                best.hi = i;
                best.width = w;
            }
        } else {
            cur_lo = -1;                   // смуга обірвалась
        }
    }
    return best;                           // best.width == 0, якщо жодної P
}
