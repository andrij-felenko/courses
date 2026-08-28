// LZW-кодування. Словник: запис = (батьківський код, байт). Рядок ніколи не
// зберігаємо цілком — лише його останній байт і номер «хвоста без останнього».
// dict[code] = {prefix, byte}; пошук "w+c" — за хешем (prefix=code(w), byte=c).
#define CLEAR 256
#define END   257
#define FIRST 258
#define MAXBITS 12
#define MAXCODE ((1 << MAXBITS) - 1)   // 4095

typedef struct { int prefix; uint8_t byte; } Entry;

// Хеш-таблиця (code(w), c) -> номер. Повертає номер або -1, якщо нема.
static int dict_lookup(int prefix, uint8_t c);          // деталі хешу опускаємо
static void dict_insert(int prefix, uint8_t c, int code);
static void dict_reset(void);                            // лишити тільки 0..255

void lzw_encode(const uint8_t *src, size_t n, BitWriter *bw) {
    dict_reset();
    int next = FIRST, width = 9;
    bits_put(bw, CLEAR, width);          // почати зі скидання — поширена угода

    int w = -1;                          // -1 = «порожній рядок»
    for (size_t i = 0; i < n; i++) {
        uint8_t c = src[i];
        if (w == -1) { w = c; continue; }    // перший байт — просто стає w
        int found = dict_lookup(w, c);
        if (found >= 0) {
            w = found;                       // wc у словнику — нарощуємо
        } else {
            bits_put(bw, w, width);          // видати код(w)
            dict_insert(w, c, next++);       // додати wc
            if (next > (1 << width) && width < MAXBITS)
                width++;                      // номер переріс ширину — +1 біт
            if (next > MAXCODE) {             // словник повний
                bits_put(bw, CLEAR, width);   // сигнал скидання
                dict_reset(); next = FIRST; width = 9;
            }
            w = c;                            // новий збіг
        }
    }
    if (w != -1) bits_put(bw, w, width);     // хвіст
    bits_put(bw, END, width);
}
