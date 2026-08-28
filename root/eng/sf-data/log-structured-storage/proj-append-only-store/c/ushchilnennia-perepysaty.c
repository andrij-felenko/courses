#define LOG_A  0x0000         // журнал A: базова адреса
#define LOG_B  0x8000         // журнал B: інший сектор, чисте місце
#define SEAL_MAGIC  0x4753454Cu   // "LSEG" — маркер печатки-покоління

// Печатка-покоління: лягає ОСТАННІМ кроком ущільнення в самий хвіст журналу.
// Активним є той журнал, чия печатка дійсна й несе БІЛЬШЕ покоління.
typedef struct {
    uint32_t magic;        // SEAL_MAGIC — щоб стерта (порожня) область не зійшла за печатку
    uint32_t generation;   // покоління: кожне ущільнення робить на 1 більше
    uint32_t crc;          // CRC від magic+generation; лягає НАЙОСТАННІШИМ — точка фіксації
} seal_t;

// Печатка живе в самому хвості області журналу; записи ростуть від бази вгору
// й ніколи в неї не залазять — тому корисна довжина журналу на печатку менша.
#define SEAL_OFF(base)  ((base) + LOG_SIZE - sizeof(seal_t))
#define LOG_END(base)   SEAL_OFF(base)          // межа дописів: до печатки, не далі

static uint32_t active_base;   // базова адреса активного журналу (LOG_A або LOG_B)
static uint32_t active_gen;    // покоління активного журналу (тримаємо в RAM)

// Печатка дійсна, лише коли є магія й CRC сходиться з magic+generation.
static int seal_valid(const seal_t *s) {
    if (s->magic != SEAL_MAGIC) return 0;              // стерта або чужа область
    return crc32(s, sizeof *s - sizeof s->crc) == s->crc;
}

// УЩІЛЬНЕННЯ: переписати живе в чистий журнал і атомарно зробити його активним.
int store_compact(void) {
    uint32_t old = active_base;
    uint32_t neu = (old == LOG_A) ? LOG_B : LOG_A;   // ущільнюємо в ІНШИЙ журнал

    flash_erase_region(neu, LOG_SIZE);               // 1) чистимо цільовий журнал (разом із його печаткою)
    uint32_t off = neu;

    // 2) переписуємо ЛИШЕ живе: покажчик — це і є перелік живих ключів
    for (int i = 0; i < MAX_KEYS; i++) {
        if (!index[i].used) continue;
        rec_hdr_t h;
        flash_read(index[i].offset, &h, sizeof h);   // читаємо чинний запис зі СТАРОГО
        uint8_t val[MAX_VAL];
        flash_read(index[i].offset + sizeof h, val, h.val_len);
        off = rec_write(off, h.key, h.key_len, val, h.val_len);  // допис у НОВИЙ (з печаткою)
        index[i].offset = off - rec_size(h.val_len);  // покажчик уже веде на місце в НОВОМУ журналі
    }

    // 3) ПЕЧАТКА-ПОКОЛІННЯ — останнім кроком: на 1 БІЛЬШЕ покоління, ніж у старого.
    //    Лягає у СВІЖОСТЕРТИЙ хвіст нового журналу (крок 1 його щойно зачистив) —
    //    тому це звичайний допис у чисте місце, а не переписування зайнятої комірки.
    seal_t sw = { .magic = SEAL_MAGIC, .generation = active_gen + 1, .crc = 0 };
    uint32_t body = sizeof sw - sizeof sw.crc;                 // magic + generation
    sw.crc = crc32(&sw, body);
    flash_write(SEAL_OFF(neu),        &sw,     body);          // спершу magic+generation
    flash_write(SEAL_OFF(neu) + body, &sw.crc, sizeof sw.crc); // а CRC — НАЙОСТАННІШИМ (точка фіксації)

    // 4) лише ТЕПЕР, коли новий несе більше покоління й цілий, стираємо старий.
    active_base = neu;
    active_gen  = sw.generation;
    write_off   = off;
    flash_erase_region(old, LOG_SIZE);
    return 0;
}
