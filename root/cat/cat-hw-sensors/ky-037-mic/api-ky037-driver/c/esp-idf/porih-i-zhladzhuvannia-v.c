static float g_smooth = 0;           // згладжений рівень (живе між ітераціями)
#define ALPHA  0.2f                  // 0..1: менше = плавніше, але млявіше

void app_main(void) {
    mic_begin();
    while (1) {
        float now = measure_rms();
        g_smooth = ALPHA * now + (1 - ALPHA) * g_smooth;   // ковзне середнє
        ESP_LOGI("ky037", "%.1f", g_smooth);
    }
}
