#define MAX_KEYS  64          // скільки РІЗНИХ ключів уміщає покажчик у RAM

typedef struct {
    char     key[KEY_LEN];    // ключ
    uint32_t offset;          // зсув його ОСТАННЬОГО запису в журналі
    uint8_t  used;            // чи зайнятий цей слот покажчика
} index_ent_t;

static index_ent_t index[MAX_KEYS];

// Знайти слот покажчика для ключа (або вільний, куди його покласти).
static index_ent_t *index_slot(const char *key, uint8_t klen) {
    index_ent_t *free_slot = NULL;
    for (int i = 0; i < MAX_KEYS; i++) {
        if (!index[i].used) {
            if (!free_slot) free_slot = &index[i];   // запам'ятали перший вільний
        } else if (memcmp(index[i].key, key, KEY_LEN) == 0) {
            return &index[i];                         // ключ уже є — його слот
        }
    }
    return free_slot;                                 // нема — віддамо вільний (або NULL)
}
