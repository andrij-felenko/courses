// АЦП-ідентифікація ревізії: подільник дає різну напругу на різні ревізії.
// Ділимо шкалу 0…4095 на вікна, по одному на ревізію, з широким запасом.

typedef struct { uint16_t center; uint8_t rev; } adc_rev_window_t;

// Центри вікон рознесені так, щоб між ними лишався зазор ширший за розкид
// резисторів. Значення center = очікуваний код АЦП для номіналів цієї ревізії.
static const adc_rev_window_t ADC_WINDOWS[] = {
    {  340, 0 },   // ≈ 0.27 В
    { 1024, 1 },   // ≈ 0.83 В  (VCC/4)
    { 2048, 2 },   // ≈ 1.65 В  (VCC/2)
    { 3072, 3 },   // ≈ 2.48 В  (3·VCC/4)
    { 3755, 4 },   // ≈ 3.03 В
};
#define ADC_WINDOW_HALF  200        // ± півширина вікна (у кодах АЦП)

// Усереднити кілька відліків АЦП — так само, як дебаунсили цифровий пін.
static uint16_t adc_read_avg(ADC_HandleTypeDef *hadc) {
    uint32_t acc = 0;
    const int N = 16;
    for (int i = 0; i < N; i++) {
        HAL_ADC_Start(hadc);
        HAL_ADC_PollForConversion(hadc, 10);
        acc += HAL_ADC_GetValue(hadc);
        HAL_ADC_Stop(hadc);
    }
    return (uint16_t)(acc / N);
}

// Знайти ревізію за виміряним рівнем; 0xFF = не потрапили в жодне вікно.
static uint8_t adc_identify_revision(ADC_HandleTypeDef *hadc) {
    uint16_t v = adc_read_avg(hadc);
    for (unsigned i = 0; i < sizeof(ADC_WINDOWS)/sizeof(ADC_WINDOWS[0]); i++) {
        int diff = (int)v - (int)ADC_WINDOWS[i].center;
        if (diff < 0) diff = -diff;
        if (diff <= ADC_WINDOW_HALF) return ADC_WINDOWS[i].rev;   // потрапили у вікно
    }
    return 0xFF;   // між вікнами — підозра на биту плату / не той номінал
}
