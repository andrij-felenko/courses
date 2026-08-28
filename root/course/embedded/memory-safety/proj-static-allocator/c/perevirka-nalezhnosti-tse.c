// Чи belongs покажчик саме нашому пулу й указує на ПОЧАТОК блоку?
static bool pool_owns(const void *blk) {
    const uint8_t *p   = (const uint8_t *)blk;
    const uint8_t *lo  = &pool_mem[0][0];
    const uint8_t *hi  = lo + (size_t)POOL_BLOCKS * POOL_BLOCK_SZ;

    if (p < lo || p >= hi) {
        return false;                    // взагалі поза межами пулу
    }
    size_t offset = (size_t)(p - lo);
    return (offset % POOL_BLOCK_SZ) == 0; // має бути рівно на межі блоку
}
