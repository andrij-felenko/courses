// зростаюча таблиця калібрування (код АЦП → °C)
const uint16_t code_lut[] = {  410, 1230, 2050, 2870, 3686 };
const float    temp_lut[] = { 0.0f, 25.0f, 50.0f, 75.0f, 100.0f };
const int      N_LUT = 5;

float temp_from_code(uint16_t code) {
    if (code <= code_lut[0])        return temp_lut[0];
    if (code >= code_lut[N_LUT-1])  return temp_lut[N_LUT-1];
    int i = 0;
    while (code > code_lut[i+1]) i++;          // знайти інтервал
    float frac = (float)(code - code_lut[i])
               / (code_lut[i+1] - code_lut[i]); // частка всередині
    return temp_lut[i] + frac * (temp_lut[i+1] - temp_lut[i]);
}
