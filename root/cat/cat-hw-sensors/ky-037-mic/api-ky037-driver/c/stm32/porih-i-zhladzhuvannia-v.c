#define NOISE_THRESHOLD  480         // 12 біт: поріг учетверо більший за 10-бітний

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_ADC1_Init();
    while (1) {
        int loud = measure_peak_to_peak();
        if (loud > NOISE_THRESHOLD) printf("ШУМНО: %d\r\n", loud);
    }
}
