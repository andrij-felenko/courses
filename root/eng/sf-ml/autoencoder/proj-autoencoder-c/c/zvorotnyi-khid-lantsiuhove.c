/* один приклад: прямий хід, похибка, зворотний хід, крок спуску.
   Повертає ½‖x̂−x‖² для цього прикладу.                          */
static double train_one(const double *x)
{
    /* ---- прямий хід ---- */
    double z[H];
    for (int j = 0; j < H; j++) {
        double s = b1[j];
        for (int k = 0; k < N; k++) s += W1[j][k] * x[k];
        z[j] = sigmoid(s);                       /* код */
    }
    double xhat[N];
    for (int i = 0; i < N; i++) {
        double s = b2[i];
        for (int j = 0; j < H; j++) s += W2[i][j] * z[j];
        xhat[i] = sigmoid(s);                    /* відновлення */
    }

    /* ---- похибка й сигнал на виході ---- */
    double L = 0.0, d_o[N];
    for (int i = 0; i < N; i++) {
        double e = xhat[i] - x[i];
        L += 0.5 * e * e;
        d_o[i] = e * xhat[i] * (1.0 - xhat[i]);  /* dL/d(вхід сигмоїди) */
    }

    /* ---- зворотний хід: сигнал на коді (СПЕРШУ, поки W2 старе) ---- */
    double d_a[H];
    for (int j = 0; j < H; j++) {
        double g = 0.0;
        for (int i = 0; i < N; i++) g += d_o[i] * W2[i][j];
        d_a[j] = g * z[j] * (1.0 - z[j]);        /* крізь σ′ коду */
    }

    /* ---- крок спуску: тепер можна псувати ваги ---- */
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < H; j++) W2[i][j] -= LR * d_o[i] * z[j];
        b2[i] -= LR * d_o[i];
    }
    for (int j = 0; j < H; j++) {
        for (int k = 0; k < N; k++) W1[j][k] -= LR * d_a[j] * x[k];
        b1[j] -= LR * d_a[j];
    }
    return L;
}
