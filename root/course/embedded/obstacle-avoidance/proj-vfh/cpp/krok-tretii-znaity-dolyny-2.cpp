typedef struct { int start; int width; } Valley;   // початковий сектор і ширина

// Зібрати всі вільні долини з бінарного кільця. Повертає їхню кількість.
int find_valleys(const uint8_t occ[N_SECTORS], Valley out[], int max_out)
{
    int count = 0;
    int k = 0;

    // Знайдемо будь-який ЗАЙНЯТИЙ сектор як точку розриву кільця,
    // щоб не розсікти долину, що лежить на стику 0 / N-1.
    int startk = -1;
    for (int i = 0; i < N_SECTORS; i++)
        if (occ[i]) { startk = i; break; }

    if (startk < 0) {                        // усе кільце вільне (чисте поле)
        if (max_out > 0) { out[0].start = 0; out[0].width = N_SECTORS; return 1; }
        return 0;
    }

    // Обходимо повне коло від першого зайнятого сектора.
    int i = 0;
    while (i < N_SECTORS && count < max_out) {
        int s = (startk + i) % N_SECTORS;
        if (!occ[s]) {                       // початок вільного пробігу
            int w = 0;
            while (i < N_SECTORS) {
                int t = (startk + i) % N_SECTORS;
                if (occ[t]) break;
                w++; i++;
            }
            if (w >= S_MIN) {                // вужчі за S_MIN — не проходимо, відкидаємо
                out[count].start = s;
                out[count].width = w;
                count++;
            }
        } else {
            i++;
        }
    }
    return count;
}
