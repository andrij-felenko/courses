// Паспортний клас приладу: a% показу + b одиниць молодшого розряду.
#define ACC_PERCENT   0.5f    // a, % показу (пропорційна частина)
#define ACC_COUNTS    2       // b, одиниць   (стала «підлога»)

// reading_mV — поточний показ, мВ;  lsd_mV — вага однієї одиниці на діапазоні, мВ
float meas_error_mV(float reading_mV, float lsd_mV) {
    float prop  = (ACC_PERCENT / 100.0f) * reading_mV;  // росте з показом
    float fl    = ACC_COUNTS * lsd_mV;                  // стала, від діапазону
    return prop + fl;                                   // повна межа похибки
}
