#define N 4                       // довжина «регістра»: 4 відводи
static int16_t line[N];           // лінія затримки: line[0]=x[n] … line[N-1]=x[n-3]
static const int16_t b[N] = {1, 1, 1, 1};   // коефіцієнти (тут — просте середнє)

// Один такт: зсунули історію, завели новий відлік, порахували вихід.
int16_t fir_step(int16_t sample) {
    for (int k = N - 1; k > 0; k--)   // зсув: усе на щабель «у минуле»
        line[k] = line[k - 1];
    line[0] = sample;                 // новий відлік x[n] — у перший відвід

    int32_t acc = 0;
    for (int k = 0; k < N; k++)       // y[n] = Σ b[k]·x[n-k]
        acc += (int32_t)b[k] * line[k];
    return acc / N;                   // ділення на суму ваг (4) — нормування
}
