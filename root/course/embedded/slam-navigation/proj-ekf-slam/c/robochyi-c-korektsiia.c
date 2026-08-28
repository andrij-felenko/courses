// Корекція ВІДОМИМ орієнтиром i: бачимо його за дальністю r, пеленгом phi.
// Оновлюємо ВЕСЬ стан і ВСЮ коваріацію — поза + усі орієнтири розом.
void slam_update(Slam *s, int i, float r, float phi, SensorNoise sn) {
    int d = s->dim;
    int o = lm_off(i);

    // 1) Очікуваний вимір h(стан) і нев'язка y = z - h.
    float dx = s->x[o]   - s->x[0];
    float dy = s->x[o+1] - s->x[1];
    float q  = dx*dx + dy*dy;
    float sq = sqrtf(q);
    float z_hat_r   = sq;
    float z_hat_phi = atan2f(dy, dx) - s->x[2];

    float y_r   = r   - z_hat_r;
    float y_phi = phi - z_hat_phi;
    // Кут — циклічний: нормуємо нев'язку пеленга в (-pi, pi], інакше «стрибок
    // через pi» дасть величезну хибну нев'язку й рвоне фільтр (див. пастки).
    y_phi = atan2f(sinf(y_phi), cosf(y_phi));

    // 2) Якобіан виміру H (2 x d): НЕНУЛЬОВИЙ лише в стовпцях пози й орієнтира i.
    //    Похідні h по (x,y,theta) і по (mx_i, my_i).
    float Hp[2][3] = {
        { -dx/sq, -dy/sq,  0.0f },
        {  dy/q,  -dx/q,  -1.0f },
    };
    float Hl[2][2] = {
        {  dx/sq,  dy/sq },
        { -dy/q,   dx/q  },
    };

    // 3) S = H*P*H^T + R (2x2). Будуємо H*P як рядок-по-стану (2 x d),
    //    використовуючи розрідженість H (тільки поза + орієнтир i).
    static float HP[2][DIM_MAX];               // 2 x d (static — не на стеку)
    for (int c=0;c<d;c++) {
        // H має блоки Hp у стовпцях 0..2 і Hl у стовпцях o..o+1.
        float a0 = Hp[0][0]*s->P[0][c] + Hp[0][1]*s->P[1][c] + Hp[0][2]*s->P[2][c]
                 + Hl[0][0]*s->P[o][c] + Hl[0][1]*s->P[o+1][c];
        float a1 = Hp[1][0]*s->P[0][c] + Hp[1][1]*s->P[1][c] + Hp[1][2]*s->P[2][c]
                 + Hl[1][0]*s->P[o][c] + Hl[1][1]*s->P[o+1][c];
        HP[0][c] = a0; HP[1][c] = a1;
    }
    float R[2][2] = { { sn.sigma_r*sn.sigma_r, 0 },
                      { 0, sn.sigma_phi*sn.sigma_phi } };
    // S = HP * H^T + R  (знову через розрідженість H — лише поза + орієнтир i).
    float S[2][2];
    for (int a=0;a<2;a++) for (int b=0;b<2;b++){
        float v = HP[a][0]*Hp[b][0] + HP[a][1]*Hp[b][1] + HP[a][2]*Hp[b][2]
                + HP[a][o]*Hl[b][0] + HP[a][o+1]*Hl[b][1];
        S[a][b] = v + R[a][b];
    }

    // 4) Обернути S (2x2) і дістати підсилення K = P*H^T*S^-1 (d x 2).
    float det = S[0][0]*S[1][1] - S[0][1]*S[1][0];
    if (fabsf(det) < 1e-12f) return;           // вироджений вимір — пропустити
    float Si[2][2] = { {  S[1][1]/det, -S[0][1]/det },
                       { -S[1][0]/det,  S[0][0]/det } };
    // (P*H^T) — це транспонована HP (бо P симетрична: P*H^T = (H*P)^T).
    static float K[DIM_MAX][2];
    for (int row=0; row<d; row++) {
        float ph0 = HP[0][row], ph1 = HP[1][row];   // (P*H^T)[row] = HP[:,row]
        K[row][0] = ph0*Si[0][0] + ph1*Si[1][0];
        K[row][1] = ph0*Si[0][1] + ph1*Si[1][1];
    }

    // 5) Оновити ВЕСЬ стан: x <- x + K*y. Виправлення тече в кожне число.
    for (int row=0; row<d; row++)
        s->x[row] += K[row][0]*y_r + K[row][1]*y_phi;
    s->x[2] = atan2f(sinf(s->x[2]), cosf(s->x[2]));   // нормувати курс

    // 6) Оновити ВСЮ коваріацію: P <- (I - K*H)*P.
    //    Через розрідженість H: (K*H)[row][col] чіпає лише стовпці пози й i,
    //    але результат K*H*P — щільний, бо K щільне. Тут і живе O(d^2).
    static float KH_P[DIM_MAX][DIM_MAX];
    for (int row=0; row<d; row++) {
        // (K*H)[row] має ненульові стовпці лише 0,1,2 та o,o+1:
        float kh0 = K[row][0]*Hp[0][0] + K[row][1]*Hp[1][0];   // стовпець 0
        float kh1 = K[row][0]*Hp[0][1] + K[row][1]*Hp[1][1];   // стовпець 1
        float kh2 = K[row][0]*Hp[0][2] + K[row][1]*Hp[1][2];   // стовпець 2
        float khO = K[row][0]*Hl[0][0] + K[row][1]*Hl[1][0];   // стовпець o
        float khP = K[row][0]*Hl[0][1] + K[row][1]*Hl[1][1];   // стовпець o+1
        for (int col=0; col<d; col++) {
            // (K*H*P)[row][col] = sum_k (K*H)[row][k] * P[k][col]
            float v = kh0*s->P[0][col] + kh1*s->P[1][col] + kh2*s->P[2][col]
                    + khO*s->P[o][col] + khP*s->P[o+1][col];
            KH_P[row][col] = v;
        }
    }
    for (int row=0; row<d; row++)
        for (int col=0; col<d; col++)
            s->P[row][col] -= KH_P[row][col];

    // 7) Примусово відновити симетрію: чисельний дрейф робить P трохи
    //    несиметричною, а це з часом валить фільтр (див. пастки).
    for (int row=0; row<d; row++)
        for (int col=row+1; col<d; col++) {
            float m = 0.5f*(s->P[row][col] + s->P[col][row]);
            s->P[row][col] = s->P[col][row] = m;
        }
}
