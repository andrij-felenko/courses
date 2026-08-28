/* Крос-валідація зі стратифікованим поділом за мітками класу. */
static cv_result cross_validate_stratified(int n, int k, int num_classes,
                                           const int *label, uint32_t seed) {
    int *fold_of   = (int *)malloc((size_t)n * sizeof(int));
    int *test      = (int *)malloc((size_t)n * sizeof(int));
    int *train_idx = (int *)malloc((size_t)n * sizeof(int));
    float *acc     = (float *)malloc((size_t)k * sizeof(float));

    stratified_split(n, k, num_classes, label, seed, fold_of);

    for (int f = 0; f < k; f++) {
        int nt = 0, ntr = 0;
        for (int i = 0; i < n; i++) {
            if (fold_of[i] == f) test[nt++]        = i;   /* іспит цього проходу */
            else                 train_idx[ntr++]  = i;   /* решта — навчання    */
        }
        train(train_idx, ntr);                            /* знову — з нуля */
        acc[f] = accuracy(test, nt);
    }

    float sum = 0.0f;
    for (int f = 0; f < k; f++) sum += acc[f];
    float mean = sum / (float)k;
    float ss = 0.0f;
    for (int f = 0; f < k; f++) { float d = acc[f] - mean; ss += d * d; }
    float sd = sqrtf(ss / (float)k);

    cv_result res = { mean, sd, k };
    free(fold_of); free(test); free(train_idx); free(acc);
    return res;
}
