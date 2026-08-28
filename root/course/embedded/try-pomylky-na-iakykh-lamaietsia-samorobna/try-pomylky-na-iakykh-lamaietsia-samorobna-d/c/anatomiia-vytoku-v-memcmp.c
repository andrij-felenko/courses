// Класична реалізація memcmp з раннім виходом
int naive_memcmp(const void *s1, const void *s2, size_t n) {
    const unsigned char *p1 = s1, *p2 = s2;
    for (size_t i = 0; i < n; i++) {
        if (p1[i] != p2[i]) {
            return p1[i] - p2[i]; // НЕГАЙНИЙ ВИХІД при першій розбіжності!
        }
    }
    return 0;
}
