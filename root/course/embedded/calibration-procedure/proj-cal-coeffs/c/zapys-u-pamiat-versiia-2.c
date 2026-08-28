#define CAL_SLOTS  2u

// КЛЮЧОВЕ: кожен слот — окремий ключ носія, тобто РІЗНЕ фізичне місце.
// Запис одного ключа не адресує байтів іншого, тож обрив живлення посеред
// запису одного слота фізично не може зачепити другий. У цьому вся гарантія.
static const char *const CAL_SLOT_KEY[CAL_SLOTS] = { "calslot0", "calslot1" };

// Низькорівневі примітиви носія: читання/запис ОДНОГО ключа (окремого місця).
// (реалізація — nvs_get_blob/nvs_set_blob+nvs_commit, або I2C-EEPROM, або FRAM)
extern bool nvm_read (const char *key, void *dst, size_t len);
extern bool nvm_write(const char *key, const void *src, size_t len);  // + commit/flush

// Прочитати seq чинного слота; 0, якщо ключа нема або слот побитий/чужий.
static uint32_t slot_seq(unsigned i)
{
    cal_store_t s;
    if (nvm_read(CAL_SLOT_KEY[i], &s, sizeof s) && store_valid(&s))
        return s.seq;
    return 0u;                                // порожній/побитий = найстаріший
}

// Запис коефіцієнтів атомарно: у СТАРІШИЙ слот, окремим записом його ключа.
bool cal_store_write(const cal_t *c)
{
    uint32_t seq0 = slot_seq(0), seq1 = slot_seq(1);

    // Писати в старіший слот (менший seq); новіший НЕ чіпаємо взагалі.
    unsigned old      = (seq0 <= seq1) ? 0u : 1u;
    uint32_t next_seq = 1u + ((seq0 > seq1) ? seq0 : seq1);

    cal_store_t fresh;
    store_pack(&fresh, c, next_seq);          // magic/version/seq/k/b/CRC

    // ОДИН запис в ОКРЕМИЙ ключ лише цього слота. Другий ключ цей виклик не
    // торкає — обрив живлення тут псує щонайбільше CAL_SLOT_KEY[old], а
    // слот-сусід у своєму місці лишається цілим зі старим калібруванням.
    return nvm_write(CAL_SLOT_KEY[old], &fresh, sizeof fresh);
}

// Підняти найновіше ЦІЛЕ калібрування; false якщо обидва слоти непридатні.
bool cal_store_read(cal_t *out)
{
    int      best     = -1;
    uint32_t best_seq = 0u;

    for (unsigned i = 0; i < CAL_SLOTS; i++) {
        cal_store_t s;
        if (!nvm_read(CAL_SLOT_KEY[i], &s, sizeof s)) continue;  // ключа нема
        if (!store_valid(&s))                         continue;  // побитий/чужий
        if (best < 0 || s.seq > best_seq) {                      // новіший ЦІЛИЙ
            best     = (int)i;
            best_seq = s.seq;
            out->k   = s.k;
            out->b   = s.b;
        }
    }
    return best >= 0;                          // жодного цілого → некалібрований
}
