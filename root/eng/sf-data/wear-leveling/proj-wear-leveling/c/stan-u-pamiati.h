typedef enum { BS_FREE = 0, BS_USED, BS_BAD } bstate_t;

static uint16_t map[N_LOG];      // LBA → номер фізичного блоку (NO_BLOCK — ще не писали)
static uint32_t ec[N_PHYS];      // лічильник стирань кожного фізичного блоку
static uint8_t  state[N_PHYS];   // FREE / USED / BAD
static uint64_t seq_next;        // номер, який дістанеться наступному запису
static uint32_t op_count;        // записів від старту — щоб рідко будити статичний крок

static uint16_t heap[N_PHYS];    // мін-купа вільних блоків за ec[]
static uint16_t hpos[N_PHYS];    // hpos[b] — де блок b сидить у heap[]; NO_BLOCK — його там нема
static int      heap_n;

static uint8_t  pbuf[PAGE_SIZE]; // єдиний буфер на сторінку — більшого не тримаємо

// Оголошення наперед: порядок розповіді не мусить диктувати порядок у файлі.
static void static_wl_step(void);
static int  block_is_clean(uint16_t b);
