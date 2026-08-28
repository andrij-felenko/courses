// ── Глобальні буфери (в ОЗП) і константи ─────────────────────────────
#define FS        20000        // частота дискретизації, Гц
#define N         2048         // вікно FFT (степінь двійки)
#define N_FEAT    23           // довжина вектора ознак: 12 смуг + 8 обвідних + 3 моменти

static int16_t  samples[N];    // сюди DMA складає відліки акселерометра
static float    feat[N_FEAT];  // вектор ознак: спектр + обвідна + RMS + куртозис

// Пороги й нормування — пораховані на квантованій моделі при калібруванні:
static float    sigma_feat[N_FEAT];   // σᵢ кожної ознаки (для зваженої похибки)
static float    mu_err, sigma_err;    // центр і розкид похибки на здоровому
static float    K = 3.0f;             // множник порога (ручка «рано ↔ тихо»)

// ── Один вимір: сигнал → ознаки → похибка → рішення ──────────────────
static float measure_once(void)
{
    make_features(samples, feat);          // вікно+FFT+демодуляція+моменти (нижче)

    // Прохід автокодера: той самий Invoke(), що в темі про інференс.
    for (int i = 0; i < N_FEAT; i++)
        model_input[i] = feat[i];
    interpreter->Invoke();                 // детермінований, сталий за часом

    // ЗВАЖЕНА похибка відновлення (Махаланобіс): промах у тихій смузі важить більше.
    float err = 0.0f;
    for (int i = 0; i < N_FEAT; i++) {
        float d = (feat[i] - model_output[i]) / sigma_feat[i];  // ділимо на σᵢ
        err += d * d;
    }
    return err / N_FEAT;
}

// ── Super-loop із робочим циклом ─────────────────────────────────────
void loop(void)
{
    start_dma_capture(samples, N);         // DMA годує буфер, ядро вільне
    wait_dma_done();                        // (тут ядро могло б спати)

    float score = measure_once();

    // Плаваючий поріг: повільно підлаштовується під дрейф здорової машини.
    update_threshold(score);                // EWMA — див. нижче

    if (score > mu_err + K * sigma_err)
        raise_alarm();                      // один біт назовні: діод чи пакет по радіо

    sleep_ms(4000);                         // робочий цикл: вимір раз на 4 с
}
