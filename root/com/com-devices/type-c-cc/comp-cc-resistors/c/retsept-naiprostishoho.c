// Прочитати дозволений струм USB-C із напруги на активному CC.
// adc_read_mv(pin) повертає напругу на піні в мілівольтах.

typedef enum { CC_NONE, CC_DEFAULT, CC_1A5, CC_3A0 } cc_level_t;

static cc_level_t cc_decode(uint16_t mv) {
    if (mv < 200)   return CC_NONE;     // < 0.20 В — нічого не під'єднано
    if (mv < 660)   return CC_DEFAULT;  // 0.20–0.66 В — звичайний USB
    if (mv < 1230)  return CC_1A5;      // 0.66–1.23 В — 1.5 А
    return CC_3A0;                       // > 1.23 В — повні 3.0 А
}

// Роз'єм реверсивний: активний той CC, на якому є напруга.
cc_level_t usbc_read_profile(void) {
    uint16_t v1 = adc_read_mv(PIN_CC1);
    uint16_t v2 = adc_read_mv(PIN_CC2);
    uint16_t cc = (v1 > v2) ? v1 : v2;   // живий пін — з вищою напругою
    return cc_decode(cc);
}
