int main(void)
{
    double X[N][N];                              /* 8 one-hot шаблонів */
    for (int s = 0; s < N; s++)
        for (int k = 0; k < N; k++)
            X[s][k] = (k == s) ? 1.0 : 0.0;

    srand(1);
    init_weights();

    for (int epoch = 0; epoch < EPOCHS; epoch++) {
        double total = 0.0;
        for (int s = 0; s < N; s++) total += train_one(X[s]);
        if (epoch % 1000 == 0 || epoch == EPOCHS - 1)
            printf("епоха %4d   середня похибка = %.4f\n", epoch, total / N);
    }

    puts("\nшаблон -> код z[3]");               /* що вивчив код */
    for (int s = 0; s < N; s++) {
        double z[H];
        for (int j = 0; j < H; j++) {
            double a = b1[j];
            for (int k = 0; k < N; k++) a += W1[j][k] * X[s][k];
            z[j] = sigmoid(a);
        }
        printf("  %d:  %.2f %.2f %.2f   ~  %d%d%d\n", s, z[0], z[1], z[2],
               (int)(z[0] + 0.5), (int)(z[1] + 0.5), (int)(z[2] + 0.5));
    }
    return 0;
}
