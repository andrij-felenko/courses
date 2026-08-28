const int MOTORS        = 4;
const int I_HOVER_EACH_A = 8;    // струм одного мотора на висінні, А
const int I_FULL_EACH_A  = 20;   // струм одного мотора на повному газі, А
const int CAP_MAH        = 5000; // ємність батареї, мА·год
const int USABLE_PCT     = 80;   // безпечно використовуємо ~80% ємності (LiPo не саджають у нуль)

// сумарний струм на висінні й на піку
int i_hover_A = MOTORS * I_HOVER_EACH_A;   // 4 * 8  = 32 А  (тримає вагу)
int i_peak_A  = MOTORS * I_FULL_EACH_A;    // 4 * 20 = 80 А  (усі на повному газі)

// потрібна C-rate = піковий струм / ємність[А·год]; ємність у А·год = CAP_MAH/1000
// щоб уникнути float: C = i_peak_A * 1000 / CAP_MAH
int c_needed = i_peak_A * 1000 / CAP_MAH;  // 80 * 1000 / 5000 = 16 C (мінімум; беремо з запасом)

// час висіння: корисна ємність[мА·год] / струм висіння[мА], у хвилинах
// корисні мА·год = CAP_MAH * USABLE_PCT / 100 ; струм у мА = i_hover_A * 1000
long usable_mah = (long)CAP_MAH * USABLE_PCT / 100;        // 4000 мА·год
int  hover_min  = (int)(usable_mah * 60 / (i_hover_A * 1000L)); // хвилини
// = 4000 * 60 / 32000 = 240000 / 32000 ≈ 7 хв
