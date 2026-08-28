// Знайти найсвіжіший блок (кандидат на «розморожування» холодних даних).
int pick_stale_cold_block(void)
{
    int best = -1;
    uint32_t best_count = UINT32_MAX;
    for (int b = 0; b < N_BLOCKS; b++) {
        if (!is_free[b] && erase_count[b] < best_count) {
            best_count = erase_count[b];   // застояний ветеран навпаки — з малим пробігом
            best = b;
        }
    }
    return best;   // його вміст переселимо, а блок пустимо під гарячий запис
}
