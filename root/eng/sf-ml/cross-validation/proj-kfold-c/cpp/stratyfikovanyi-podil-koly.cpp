/* Стратифікований поділ n прикладів на k блоків за мітками класу.
   label[i] — клас прикладу i, значення 0..num_classes-1.
   Заповнює fold_of[i] = номер блоку (0..k-1), куди потрапив приклад i.
   Пропорція класів у кожному блоці ≈ пропорція в усьому наборі. */
static void stratified_split(int n, int k, int num_classes,
                             const int *label, uint32_t seed, int *fold_of) {
    /* buckets[c] збиратиме індекси прикладів класу c */
    int **buckets = (int **)malloc((size_t)num_classes * sizeof(int *));
    int  *cnt     = (int  *)calloc((size_t)num_classes, sizeof(int));

    for (int i = 0; i < n; i++) cnt[label[i]]++;            /* скільки в кожнім класі */
    for (int c = 0; c < num_classes; c++)
        buckets[c] = (int *)malloc((size_t)(cnt[c] ? cnt[c] : 1) * sizeof(int));

    int *pos = (int *)calloc((size_t)num_classes, sizeof(int));
    for (int i = 0; i < n; i++) {                           /* розклали по відрах */
        int c = label[i];
        buckets[c][pos[c]++] = i;
    }

    rng_seed(seed);
    for (int c = 0; c < num_classes; c++)
        shuffle(buckets[c], cnt[c]);                        /* перемішали КОЖЕН клас */

    /* роздача по колу: приклад j класу c → блок (j % k).
       старт кола зсуваємо на клас, щоб залишки різних класів не сідали всі в блок 0 */
    for (int c = 0; c < num_classes; c++)
        for (int j = 0; j < cnt[c]; j++)
            fold_of[buckets[c][j]] = (j + c) % k;

    for (int c = 0; c < num_classes; c++) free(buckets[c]);
    free(buckets); free(cnt); free(pos);
}
