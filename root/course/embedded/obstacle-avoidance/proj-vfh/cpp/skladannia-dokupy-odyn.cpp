// Стан, що ЖИВЕ між тактами (для гістерезису бінаризації).
static uint8_t g_occ[N_SECTORS] = {0};   // 0 = вільно, стартуємо «усе вільно»

// Один такт VFH: кільце дальностей + напрям на ціль → кермовий кут.
float vfh_tick(const Ray rays[N_SECTORS], float goal_angle)
{
    float hist[N_SECTORS];
    float smooth[N_SECTORS];
    Valley valleys[N_SECTORS / 2];        // долин не буває більше, ніж пів-кільця

    build_histogram(rays, hist);          // 1) сирі дальності → щільність
    smooth_histogram(hist, smooth, 2);    // 2) згладити (L = 2)
    binarize_hysteresis(smooth, g_occ);   // 3) два пороги → бінарне кільце (з пам'яттю)

    int nv = find_valleys(g_occ, valleys, N_SECTORS / 2);   // 4a) зібрати долини
    return vfh_steer(valleys, nv, goal_angle);              // 4b) вибрати й видати кут
}
