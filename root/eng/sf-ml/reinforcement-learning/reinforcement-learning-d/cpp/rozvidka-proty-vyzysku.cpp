#include <stdlib.h>

// вибір дії: з імовірністю eps — випадкова (розвідка),
// інакше — з найбільшим Q (визиск)
int choose_action(const float *q_row, int A, float eps)
{
    // rand()/RAND_MAX — псевдовипадкове число в [0,1)
    if ((float)rand() / RAND_MAX < eps)
        return rand() % A;              // розвідка: будь-яка дія

    int best = 0;                       // визиск: argmax по Q
    for (int j = 1; j < A; ++j)
        if (q_row[j] > q_row[best])
            best = j;
    return best;
}
