// C ≥ 2·P·t_hold / (Vbus² − Vmin²)
float P      = 300.0f;      // потужність, Вт
float t_hold = 20e-3f;      // час утримання, с (один період 50 Гц)
float Vbus   = 400.0f;      // робоча напруга шини, В
float Vmin   = 320.0f;      // мінімум, до якого тримає DC-DC, В

float C_min = 2.0f * P * t_hold / (Vbus*Vbus - Vmin*Vmin);
// = 2·300·0.020 / (160000 − 102400)
// = 12.0 / 57600
// ≈ 208e-6 Ф = 208 мкФ
