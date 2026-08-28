// Тензоваги: in-amp із G = 400, АЦП 12 біт, опорна 5.000 В.
// Чутливість моста 2 мВ/В при 5 В живлення → повна шкала = 4.000 В на виході.
constexpr float kAdcRefV   = 5.0f;
constexpr float kAdcMax    = 4095.0f;
constexpr float kInampGain = 400.0f;
constexpr float kBridgeFsV = 0.010f;   // 10 мВ диференційного при повній шкалі
constexpr float kScaleFsKg = 20.0f;    // повна шкала терезів, кг

constexpr float weight_kg(std::uint16_t adc_code)
{
    const float v_out  = (adc_code / kAdcMax) * kAdcRefV;  // напруга на виході in-amp
    const float v_diff = v_out / kInampGain;               // зведено до входу (диф.)
    const float frac   = v_diff / kBridgeFsV;              // частка повної шкали
    return frac * kScaleFsKg;                              // вага
}
