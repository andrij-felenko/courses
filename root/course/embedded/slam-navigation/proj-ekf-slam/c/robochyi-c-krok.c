// Шум руху (process noise): наскільки брехливі dr і d(theta) за один такт.
// Це «довіра до одометрії» — більший шум = швидше роздувається невпевненість.
typedef struct { float sigma_dr; float sigma_dth; } MotionNoise;

// Передбачення: проїхали dr уперед, повернули dth. Штовхаємо позу й
// РОЗДУВАЄМО невпевненість — у т.ч. кореляції пози з кожним орієнтиром.
void slam_predict(Slam *s, float dr, float dth, MotionNoise mn) {
    float th  = s->x[2];
    float thm = th + 0.5f*dth;            // середній курс на такті
    float c = cosf(thm), sn = sinf(thm);

    // 1) Просунути САМУ позу (орієнтири не рухаються).
    s->x[0] += dr * c;
    s->x[1] += dr * sn;
    s->x[2]  = atan2f(sinf(th + dth), cosf(th + dth));  // тримаємо у (-pi, pi]

    // 2) Якобіан руху по позі Fx (3x3): d(нова поза)/d(стара поза).
    //    Похідні моделі вище. Поза міняється — орієнтири ні, тож решта = I.
    float Fx[3][3] = {
        { 1.0f, 0.0f, -dr * sn },     // dx'/dtheta = -dr*sin(thm)
        { 0.0f, 1.0f,  dr * c  },     // dy'/dtheta =  dr*cos(thm)
        { 0.0f, 0.0f,  1.0f    },
    };

    // 3) Коваріація руху Q (3x3) у просторі пози: невизначеність dr, dth.
    //    Грубо, але робоче: розкладаємо шум кроку по осях через той самий якобіан руху.
    float Q[3][3] = {0};
    float vr = mn.sigma_dr * mn.sigma_dr;     // дисперсія поздовжнього кроку
    float vt = mn.sigma_dth * mn.sigma_dth;   // дисперсія повороту
    Q[0][0] = vr*c*c    + vt*(dr*sn)*(dr*sn);
    Q[1][1] = vr*sn*sn  + vt*(dr*c )*(dr*c );
    Q[0][1] = Q[1][0] = vr*c*sn - vt*(dr*c)*(dr*sn);
    Q[2][2] = vt;

    int d = s->dim;

    // 4) Оновити блок пози: Ppp <- Fx*Ppp*Fx^T + Q   (верхній лівий 3x3).
    float Ppp[3][3], tmp[3][3];
    for (int i=0;i<3;i++) for (int j=0;j<3;j++) Ppp[i][j] = s->P[i][j];
    // tmp = Fx*Ppp
    for (int i=0;i<3;i++) for (int j=0;j<3;j++){
        float a=0; for(int k=0;k<3;k++) a += Fx[i][k]*Ppp[k][j]; tmp[i][j]=a; }
    // Ppp = tmp*Fx^T + Q
    for (int i=0;i<3;i++) for (int j=0;j<3;j++){
        float a=0; for(int k=0;k<3;k++) a += tmp[i][k]*Fx[j][k];
        s->P[i][j] = a + Q[i][j]; }

    // 5) КЛЮЧОВЕ: оновити кроскореляції пози з КОЖНИМ орієнтиром.
    //    Стовпці орієнтирів у рядках пози: Ppm <- Fx*Ppm  (і дзеркально Pmp).
    //    Саме тут зросла невпевненість пози «затікає» в усю карту.
    for (int col=POSE_N; col<d; col++) {
        float v0=s->P[0][col], v1=s->P[1][col], v2=s->P[2][col];
        for (int i=0;i<3;i++) {
            float a = Fx[i][0]*v0 + Fx[i][1]*v1 + Fx[i][2]*v2;
            s->P[i][col] = a;       // рядок пози ↔ стовпець орієнтира
            s->P[col][i] = a;       // симетрія: дзеркальний елемент той самий
        }
    }
}
