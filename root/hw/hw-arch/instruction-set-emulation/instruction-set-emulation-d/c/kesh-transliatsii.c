#define TB_CACHE_SIZE 65536
#define TB_HASH(pc) (((pc) ^ ((pc) >> 6)) & (TB_CACHE_SIZE - 1))

static TranslationBlock *tb_cache[TB_CACHE_SIZE];

TranslationBlock *tb_find(uint32_t guest_pc) {
    uint32_t hash = TB_HASH(guest_pc);
    TranslationBlock *tb = tb_cache[hash];
    if (tb && tb->guest_pc == guest_pc) {
        return tb; // Влучання в кеш (Cache Hit)
    }
    return NULL;   // Промах (Cache Miss) — необхідна JIT-трансляція
}
