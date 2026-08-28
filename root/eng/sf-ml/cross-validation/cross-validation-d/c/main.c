#include <stdio.h>

#define N 200      /* усього прикладів */
#define K 5        /* число блоків     */

/* Твої функції моделі (заглушки під конкретний алгоритм):
   train  — навчити на вибраних індексах;
   accuracy — частка правильних на вибраних індексах. */
void  train(const int *idx, int n);
float accuracy(const int *idx, int n);

int order[N];      /* перемішаний порядок прикладів 0..N-1 */

float cross_validate(void)
{
    int fold_size = N / K;          /* 200 / 5 = 40 у блоці */
    float sum = 0.0f;

    for (int f = 0; f < K; f++) {
        int test[N], train_idx[N];
        int nt = 0, ntr = 0;

        int lo = f * fold_size;             /* межі f-го блоку */
        int hi = lo + fold_size;

        for (int i = 0; i < N; i++) {
            if (i >= lo && i < hi)          /* цей блок — «іспит» */
                test[nt++] = order[i];
            else                            /* решта — навчання   */
                train_idx[ntr++] = order[i];
        }

        train(train_idx, ntr);              /* навчаємо з нуля     */
        float a = accuracy(test, nt);       /* міряємо на іспиті   */
        sum += a;
        printf("прохід %d: %.1f%%\n", f + 1, a * 100.0f);
    }
    return sum / K;                         /* середнє п'яти чисел */
}
