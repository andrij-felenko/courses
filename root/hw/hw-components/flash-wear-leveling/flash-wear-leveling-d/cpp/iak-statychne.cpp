#define GAP_THRESHOLD 512   // допустимий розрив пробігу між блоками

// Чи час зрівнювати знос примусово?
int need_static_leveling(void)
{
    uint32_t lo = UINT32_MAX, hi = 0;
    for (int b = 0; b < N_BLOCKS; b++) {
        if (erase_count[b] < lo) lo = erase_count[b];   // наймолодший
        if (erase_count[b] > hi) hi = erase_count[b];   // найстаріший
    }
    return (hi - lo) > GAP_THRESHOLD;   // розрив завеликий → пора переселяти
}
