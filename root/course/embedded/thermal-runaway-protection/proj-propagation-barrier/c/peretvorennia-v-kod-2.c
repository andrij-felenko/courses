// Медіана температур зон — стійкий «фон» пакета (копіюємо, щоб не псувати вхід).
static int32_t zones_median(const int32_t *t_c10, int n) {
    int32_t buf[N_ZONES];
    for (int i = 0; i < n; i++) buf[i] = t_c10[i];
    for (int i = 1; i < n; i++) {            // сортування вставками — для 8 зон швидше за все
        int32_t key = buf[i]; int j = i - 1;
        while (j >= 0 && buf[j] > key) { buf[j + 1] = buf[j]; j--; }
        buf[j + 1] = key;
    }
    return buf[n / 2];
}
