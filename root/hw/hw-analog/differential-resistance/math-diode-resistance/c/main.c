// диференційний опір ідеального переходу: r = U_T / I
const float U_T = 0.026f;        // 26 мВ при кімнатній температурі

float r_junction(float I) {      // I в амперах -> r в омах
    return U_T / I;
}

float ra = r_junction(0.0001f);  // 0.1 мА:  0.026 / 0.0001 = 260 Ом
float rb = r_junction(0.001f);   //   1 мА:  0.026 / 0.001  =  26 Ом
float rc = r_junction(0.010f);   //  10 мА:  0.026 / 0.010  = 2.6 Ом
