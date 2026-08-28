/* Алгоритм Кахана для високоточного підсумовування суперпозиції */
typedef struct {
    double sum;        /* Накопичена сума */
    double comp;       /* Компенсація втрачених молодших розрядів */
} KahanAccumulator;

inline void kahan_add(KahanAccumulator *acc, double input) {
    double y = input - acc->comp;
    double t = acc->sum + y;
    acc->comp = (t - acc->sum) - y;
    acc->sum = t;
}
