/* Практичний розв'язок задачі рюкзака через LLL */
void solve_knapsack(const int64_t *weights, int n, int64_t target_sum) {
    int dim = n + 1;
    IntMatrix B = create_int_matrix(dim, dim);
    int64_t N = (int64_t)ceil(0.5 * sqrt((double)n)) + 10;

    /* Заповнення матриці ґратки */
    for (int i = 0; i < n; i++) {
        B.data[i][i] = 2;
        B.data[i][n] = 2 * N * weights[i];
    }
    for (int j = 0; j < n; j++) {
        B.data[n][j] = 1;
    }
    B.data[n][n] = 2 * N * target_sum;

    /* Виклик LLL-редукції */
    lll_reduce(&B, LLL_DELTA);

    /* Пошук вектора розв'язку */
    bool found = false;
    for (int row = 0; row < dim; row++) {
        if (B.data[row][n] == 0) {
            bool valid = true;
            for (int j = 0; j < n; j++) {
                if (abs((int)B.data[row][j]) != 1) {
                    valid = false;
                    break;
                }
            }
            if (valid) {
                printf("Знайдено секретний бітовий вектор x: [ ");
                for (int j = 0; j < n; j++) {
                    int bit = (B.data[row][0] > 0) ? (B.data[row][j] > 0 ? 1 : 0) : (B.data[row][j] < 0 ? 1 : 0);
                    printf("%d ", bit);
                }
                printf("]\n");
                found = true;
                break;
            }
        }
    }

    if (!found) {
        printf("Розв'язок не знайдено (потрібна вища щільність або більший параметр delta).\n");
    }

    free_int_matrix(&B);
}

int main(void) {
    /* Приклад: рюкзак з 8 вагами */
    int64_t weights[8] = {102, 205, 412, 825, 1653, 3310, 6625, 13254};
    /* Повідомлення x = (1, 0, 1, 1, 0, 1, 0, 1) */
    /* Цільова сума S = 102 + 412 + 825 + 3310 + 13254 = 17903 */
    int64_t S = 17903;

    printf("Криптоаналіз рюкзака Меркля — Геллмана через LLL:\n");
    printf("Цільова сума S = %lld\n", (long long)S);
    solve_knapsack(weights, 8, S);

    return 0;
}
