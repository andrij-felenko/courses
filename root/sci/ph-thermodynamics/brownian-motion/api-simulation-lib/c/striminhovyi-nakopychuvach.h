typedef struct {
    double *msd_sum;      /* Масив накопичених сум квадрата зсуву */
    size_t *sample_count; /* Масив кількості відліків */
    size_t num_lags;      /* Кількість проміжків часу */
} BrownianStreamAccumulator;

int brownian_stream_init(BrownianStreamAccumulator *acc, size_t num_lags);
int brownian_stream_push_step(BrownianStreamAccumulator *acc, size_t lag, double dx, double dy, double dz);
int brownian_stream_finalize(const BrownianStreamAccumulator *acc, BrownianMsdResult *out_result);
void brownian_stream_free(BrownianStreamAccumulator *acc);
