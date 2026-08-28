// Наскрізна перевірка: геш потоку, який ведуть тільки два кінці.
struct Fnv1a {
    uint64_t h = 0xcbf29ce484222325ull;          // початковий стан FNV-1a 64
    void feed(const uint8_t* p, size_t n) {
        for (size_t i = 0; i < n; ++i) {
            h ^= p[i];
            h *= 0x100000001b3ull;               // просте число FNV
        }
    }
};
