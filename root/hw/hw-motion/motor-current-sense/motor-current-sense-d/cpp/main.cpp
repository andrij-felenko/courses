// Вимір струму BLDC: 3 шунти low-side, центрований ШІМ, відлік у центрі періоду.
// АЦП запускається таймером ШІМ; тут — обробник «перетворення завершено».
#include <cstdint>
#include <atomic>

constexpr float R_SHUNT = 0.005f;   // Ом, шунт під пік струму
constexpr float GAIN    = 20.0f;    // коефіцієнт підсилювача струму
constexpr float VREF    = 3.3f;     // опорна напруга АЦП, В
constexpr float ADC_FS  = 4096.0f;  // повна шкала 12-біт АЦП

// Калібровані «нулі» (код АЦП при I=0): двонапрямлений вимір, нуль ≈ середина шкали.
static std::uint16_t zero_a = 2048, zero_c = 2048;

// Код АЦП фази → струм у амперах (з урахуванням зсунутого нуля).
inline float adc_to_current(std::uint16_t raw, std::uint16_t zero) {
    float v_out = (static_cast<int>(raw) - static_cast<int>(zero)) * (VREF / ADC_FS);  // напруга від нуля, В
    float v_sh  = v_out / GAIN;                                                         // спад на шунті, В
    return v_sh / R_SHUNT;                                                              // I = V/R (зі знаком)
}

std::atomic<float> ia, ib, ic;    // миттєві струми фаз, А

void ADC_ConvCplt_IRQHandler(std::uint16_t raw_a, std::uint16_t raw_c) {
    float a = adc_to_current(raw_a, zero_a);   // фаза A з її шунта
    float c = adc_to_current(raw_c, zero_c);   // фаза C з її шунта
    ia = a; ic = c;
    ib = -(a + c);                             // фаза B — з правила суми нуль
    // далі: ia, ib, ic → у контур керування моментом (напр. Кларк/Парк для FOC)
}

// Калібрування нулів: викликати при гарантовано знеструмленому моторі.
void calibrate_zero(std::uint16_t raw_a, std::uint16_t raw_c) {
    static std::uint32_t acc_a = 0, acc_c = 0;
    static int n = 0;
    acc_a += raw_a; acc_c += raw_c;
    if (++n == 256) { zero_a = acc_a / 256; zero_c = acc_c / 256; n = 0; acc_a = acc_c = 0; }
}
