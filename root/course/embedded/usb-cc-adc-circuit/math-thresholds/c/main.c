// Канон і запас зведені в один розрахунок порогів переходу 1.5А↔3.0А.
// Усі величини в мВ — у тих самих одиницях, у яких АЦП віддає число.
#define CC_NOISE_PP    80    // розмах залишкового шуму після RC+усереднення, мВ
#define CC_GAP_HIGH    300   // зазор між смугами 1.5А і 3.0А, мВ
#define CC_CENTER_HIGH 1230  // середина зазору = центр переходу, мВ

// Смугу беремо ~1.75× ширшою за шум, але не ширшою за зазор.
#define CC_BAND_HIGH   ((CC_NOISE_PP * 7 / 4 < CC_GAP_HIGH) ? CC_NOISE_PP * 7 / 4 : CC_GAP_HIGH)
//                       80·1.75 = 140 мВ  <  300 мВ  →  беремо 140

static const int THR_UP_HIGH = CC_CENTER_HIGH + CC_BAND_HIGH / 2;  // 1230 + 70 = 1300
static const int THR_DN_HIGH = CC_CENTER_HIGH - CC_BAND_HIGH / 2;  // 1230 − 70 = 1160
