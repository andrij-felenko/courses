// Згладжування гістограми трикутним вікном (±L секторів).
// Кільце замкнене: сектор 0 сусідить із сектором N_SECTORS-1.
void smooth_histogram(const float in[N_SECTORS], float out[N_SECTORS], int L)
{
    // Трикутні ваги: центр = L+1, далі спадають до 1. Сума ваг = (L+1)².
    float wsum = (float)((L + 1) * (L + 1));

    for (int k = 0; k < N_SECTORS; k++) {
        float acc = 0.0f;
        for (int j = -L; j <= L; j++) {
            int idx = (k + j + N_SECTORS) % N_SECTORS;   // замкнене коло
            int w   = (L + 1) - (j < 0 ? -j : j);        // трикутна вага
            acc += w * in[idx];
        }
        out[k] = acc / wsum;
    }
}
