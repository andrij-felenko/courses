// Монітор струму на ESP32: шунт 5 мОм + підсилювач G=50 + 12-біт АЦП
const float R_SHUNT = 0.005f;     // Ом
const float GAIN    = 50.0f;      // коефіцієнт підсилювача струму
const float VREF    = 3.3f;       // опорна напруга АЦП, В
const int   ADC_MAX = 4095;       // 12 біт
float i_zero = 0.0f;              // калібрований нуль (привид від offset), А
double charge_mAh = 0.0;          // накопичений заряд

// Перевести «сирий» код АЦП у струм через шунт (закон Ома, назад через тракт)
float readCurrent() {
    int   raw   = analogRead(34);                 // вхід підсилювача → АЦП
    float v_adc = (float)raw / ADC_MAX * VREF;    // напруга на вході АЦП, В
    float v_sh  = v_adc / GAIN;                    // спад на самому шунті, В
    return v_sh / R_SHUNT - i_zero;               // I = V/R, мінус нуль
}

// Калібрування нуля: викликати, коли точно відомо, що струму немає
void calibrateZero() {
    float acc = 0.0f;
    for (int k = 0; k < 64; k++) { acc += readCurrent() + i_zero; delay(2); }
    i_zero = acc / 64.0f;                          // усереднений привид від offset
}

// Інтегрувати заряд: Q += I·Δt  (coulomb counter)
void accumulateCharge(float dt_s) {
    float i = readCurrent();
    charge_mAh += (double)i * dt_s / 3.6;          // А·с → мА·год: ділимо на 3.6
}
