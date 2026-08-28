#include <stdint.h>

#define N 5
// Плавний профіль ваг (трикутник): менше «дзвону», ніж у рівного середнього.
static const int16_t b[N] = {1, 2, 3, 2, 1};
static const int32_t GAIN = 1 + 2 + 3 + 2 + 1;   // сума ваг = 9 → нормування

static int16_t line[N];   // лінія затримки: line[0]=x[n] … line[N-1]=x[n-4]

// Один такт FIR: зсунути історію, завести відлік, порахувати зважену суму.
int16_t fir_step(int16_t sample) {
    for (int k = N - 1; k > 0; k--)   // зсув «у минуле» — це фронт такту
        line[k] = line[k - 1];
    line[0] = sample;                 // новий відлік у перший відвід

    int32_t acc = 0;                  // ширший тип: сума може перерости 16 біт
    for (int k = 0; k < N; k++)       // y[n] = Σ b[k]·x[n-k]
        acc += (int32_t)b[k] * line[k];

    return (int16_t)(acc / GAIN);     // ділення на суму ваг — щоб рівень не поплив
}
