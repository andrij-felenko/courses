/* Результат крос-валідації: середнє й розкид точностей по проходах. */
typedef struct { float mean; float sd; int k; } cv_result;

/* Твої функції моделі (заглушки під конкретний алгоритм):
   train    — навчити модель з нуля на прикладах idx[0..n-1];
   accuracy — частка правильних на прикладах idx[0..n-1] (0..1). */
extern void  train(const int *idx, int n);
extern float accuracy(const int *idx, int n);

/* k-кратна крос-валідація над n прикладами. seed фіксує поділ.
   Повертає середнє й стандартне відхилення точностей k проходів. */
static cv_result cross_validate(int n, int k, uint32_t seed) {
    int *order = (int *)malloc((size_t)n * sizeof(int));
    int *test  = (int *)malloc((size_t)n * sizeof(int));
    int *train_idx = (int *)malloc((size_t)n * sizeof(int));
    float *acc = (float *)malloc((size_t)k * sizeof(float));

    for (int i = 0; i < n; i++) order[i] = i;   /* 0,1,2,…,n-1 */
    rng_seed(seed);
    shuffle(order, n);                          /* перемішали РАЗ наперед */

    for (int f = 0; f < k; f++) {
        int lo = fold_start(n, k, f);
        int hi = lo + fold_size(n, k, f);       /* [lo, hi) — «іспитовий» блок */

        int nt = 0, ntr = 0;
        for (int i = 0; i < n; i++) {
            if (i >= lo && i < hi) test[nt++]      = order[i];   /* іспит  */
            else                   train_idx[ntr++] = order[i];  /* навч.  */
        }

        train(train_idx, ntr);                  /* НАВЧАЄМО З НУЛЯ щоразу */
        acc[f] = accuracy(test, nt);            /* міряємо на відкладеному */
    }

    /* середнє */
    float sum = 0.0f;
    for (int f = 0; f < k; f++) sum += acc[f];
    float mean = sum / (float)k;

    /* розкид: √( (1/k) · Σ(acc[f] − mean)² ) */
    float ss = 0.0f;
    for (int f = 0; f < k; f++) {
        float d = acc[f] - mean;
        ss += d * d;
    }
    float sd = sqrtf(ss / (float)k);

    cv_result res = { mean, sd, k };
    free(order); free(test); free(train_idx); free(acc);
    return res;
}
