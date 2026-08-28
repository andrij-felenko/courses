static float g_smooth = 0;           // згладжений рівень (живе між ітераціями)
#define ALPHA  0.2f                  // 0..1: менше = плавніше, але млявіше

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_ADC1_Init();
    while (1) {
        float now = measure_rms();
        g_smooth = ALPHA * now + (1 - ALPHA) * g_smooth;   // ковзне середнє
        printf("%.1f\r\n", g_smooth);
    }
}
