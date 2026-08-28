// Терморезистор у нижньому плечі дільника, послідовний R зверху.
// АЦП рейтіометричний: опорний вхід = та сама шина, що живить дільник.
// Тому Vж/Vref у математику не входить узагалі.
#define ADC_FULL_SCALE  4096u     // 2^12
#define R_SERIES_OHMS   10000.0f  // постійний резистор плеча

float thermistor_ohms(uint16_t code)
{
    // Захист від ділення на нуль на самому краю шкали.
    if (code == 0u || code >= ADC_FULL_SCALE)
        return 0.0f;                       // давач закорочений або обірваний

    // R_дав = R · code / (FS − code)  — чисте відношення, без вольтів.
    return R_SERIES_OHMS * (float)code / (float)(ADC_FULL_SCALE - code);
}
