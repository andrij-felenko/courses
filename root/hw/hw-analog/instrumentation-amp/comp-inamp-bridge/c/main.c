// Тензоваги: in-amp із G = 400, АЦП 12 біт, опорна 5.000 В.
// Чутливість моста 2 мВ/В при 5 В живлення → повна шкала = 4.000 В на виході.
#define ADC_REF_V     5.0f
#define ADC_MAX       4095.0f
#define INAMP_GAIN    400.0f
#define BRIDGE_FS_V   0.010f     // 10 мВ диференційного при повній шкалі
#define SCALE_FS_KG   20.0f      // повна шкала терезів, кг

float weight_kg(uint16_t adc_code)
{
    float v_out  = (adc_code / ADC_MAX) * ADC_REF_V;   // напруга на виході in-amp
    float v_diff = v_out / INAMP_GAIN;                  // зведено до входу (диф.)
    float frac   = v_diff / BRIDGE_FS_V;               // частка повної шкали
    return frac * SCALE_FS_KG;                          // вага
}
