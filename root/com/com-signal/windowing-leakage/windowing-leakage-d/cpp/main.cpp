/* Вікно Ганна: w[n] = 0.5 − 0.5·cos(2π·n / (N−1)).
   Будуємо таблицю РАЗ при старті; далі лише множимо. */
#define N 64
static float w[N];

void hann_init(void)
{
    for (int n = 0; n < N; n++)
        w[n] = 0.5f - 0.5f * cosf(2.0f * 3.14159265f * n / (N - 1));
}

/* Перед кожним ШПФ: поелементно домножуємо запис на вікно — один прохід. */
void apply_window(float *x)
{
    for (int n = 0; n < N; n++)
        x[n] *= w[n];
}
