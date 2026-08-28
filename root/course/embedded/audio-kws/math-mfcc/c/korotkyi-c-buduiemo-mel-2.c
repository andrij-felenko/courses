// лог-мел → MFCC (лише для КЛАСИЧНОГО класифікатора; для CNN НЕ треба)
#define N_MFCC 13
void mfcc_from_logmel(const float logmel[N_MEL], float mfcc[N_MFCC]) {
    for (int j = 0; j < N_MFCC; j++) {
        float acc = 0.0f;
        for (int i = 0; i < N_MEL; i++)
            acc += logmel[i] * cosf((float)M_PI * j * (i + 0.5f) / N_MEL);  // DCT-II
        mfcc[j] = acc;
    }
}
