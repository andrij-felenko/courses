const int N = 8;                 // діодів у ряду
const uint8_t pins[N] = {2,4,5,12,13,14,15,16};

void chaseTick(unsigned long now) {
    float head = (now % 1600) / 1600.0f * N;   // позиція гребеня 0..N, циклічно
    for (int i = 0; i < N; i++) {
        float d = fabsf(i - head);
        if (d > N / 2) d = N - d;               // стрічка замкнена в кільце
        float bright = (d < 1.5f) ? (1.0f - d / 1.5f) : 0.0f;  // згасання від гребеня
        ledcWrite(pins[i], gammaLUT[(uint8_t)(bright * 255)]);
    }
}
