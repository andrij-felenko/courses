// Шум давача range-bearing: похибка дальності й пеленга одного виміру.
typedef struct { float sigma_r; float sigma_phi; } SensorNoise;

// Вписати НОВИЙ орієнтир (дальність r, пеленг phi) у спільний стан.
// Стан росте на 2; новий блок ОДРАЗУ скорельований із позою.
// Повертає індекс орієнтира або -1, якщо карта повна.
int slam_add_landmark(Slam *s, int id, float r, float phi, SensorNoise sn) {
    if (s->n_lm >= LM_MAX) return -1;           // фіксована пам'ять — без malloc
    int i  = s->n_lm;
    int o  = lm_off(i);                         // зсув mx_i у векторі стану
    float th = s->x[2];
    float ca = cosf(th + phi), sa = sinf(th + phi);

    // 1) Координати нового орієнтира зі своєї пози й виміру.
    s->x[o    ] = s->x[0] + r*ca;
    s->x[o + 1] = s->x[1] + r*sa;

    // 2) Якобіани функції народження g(pose, r, phi):
    //    Gp = dg/d(pose)  (2x3) — як координати орієнтира залежать від пози;
    //    Gz = dg/d(r,phi) (2x2) — як вони залежать від самого виміру.
    float Gp[2][3] = {
        { 1.0f, 0.0f, -r*sa },
        { 0.0f, 1.0f,  r*ca },
    };
    float Gz[2][2] = {
        { ca, -r*sa },
        { sa,  r*ca },
    };
    float R[2][2] = { { sn.sigma_r*sn.sigma_r, 0 },
                      { 0, sn.sigma_phi*sn.sigma_phi } };

    int d = s->dim;

    // 3) Коваріація нового орієнтира: Pmm = Gp*Ppp*Gp^T + Gz*R*Gz^T.
    //    Перший доданок — успадкована невпевненість пози (СПІЛЬНА помилка!),
    //    другий — власний шум цього виміру.
    float Ppp[3][3];
    for (int a=0;a<3;a++) for (int b=0;b<3;b++) Ppp[a][b]=s->P[a][b];
    float GpP[2][3];
    for (int a=0;a<2;a++) for (int b=0;b<3;b++){
        float v=0; for(int k=0;k<3;k++) v+=Gp[a][k]*Ppp[k][b]; GpP[a][b]=v; }
    for (int a=0;a<2;a++) for (int b=0;b<2;b++){
        float v=0; for(int k=0;k<3;k++) v+=GpP[a][k]*Gp[b][k];          // Gp*Ppp*Gp^T
        float w=0;                                                     // Gz*R*Gz^T
        for(int k=0;k<2;k++) for(int l=0;l<2;l++) w+=Gz[a][k]*R[k][l]*Gz[b][l];
        s->P[o+a][o+b] = v + w;
    }

    // 4) КРОСКОРЕЛЯЦІЯ нового орієнтира з рештою стану: Pmrest = Gp*Prest.
    //    Через позу новий орієнтир одразу зв'язується з УСІМ, що вже в карті.
    for (int col=0; col<d; col++) {
        float v0=s->P[0][col], v1=s->P[1][col], v2=s->P[2][col];
        for (int a=0;a<2;a++) {
            float v = Gp[a][0]*v0 + Gp[a][1]*v1 + Gp[a][2]*v2;
            s->P[o+a][col] = v;     // рядок нового орієнтира
            s->P[col][o+a] = v;     // симетричний стовпець
        }
    }

    // 5) Зафіксувати ріст стану.
    s->lm_id[i] = id;
    s->n_lm += 1;
    s->dim  = POSE_N + 2*s->n_lm;
    return i;
}
