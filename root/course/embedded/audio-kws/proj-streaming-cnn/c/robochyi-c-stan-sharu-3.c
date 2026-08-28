#define N_LAYERS 4

static ConvLayer net[N_LAYERS];     // ініціюються вагами/масштабами при старті

// Проганяє одну нову вхідну колонку крізь увесь стос causal-згорток.
// Повертає true й кладе фінальну колонку активацій у out[], коли ВСІ шари
// прогрілися; інакше false (мережа ще набирає контекст).
static bool net_stream_step(const int8_t input_col[], int8_t out[], int *out_len) {
    static int8_t bufA[COUT_MAX], bufB[COUT_MAX];
    const int8_t *src = input_col;
    int8_t *dst = bufA;
    for (int l = 0; l < N_LAYERS; l++) {
        if (!conv_step(&net[l], src, dst))
            return false;                       // цей шар ще прогрівається — виходимо
        src = dst;                              // вихід шару = вхід наступного
        dst = (dst == bufA) ? bufB : bufA;      // пінг-понг двох буферів колонок
    }
    memcpy(out, src, net[N_LAYERS - 1].cout * sizeof(int8_t));
    *out_len = net[N_LAYERS - 1].cout;
    return true;
}
