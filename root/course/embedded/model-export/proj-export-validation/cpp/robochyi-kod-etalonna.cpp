// Один приклад: вхідний кадр + еталонний вихід оригіналу + істинний клас.
struct TestCase {
    Frame frame;                       // вхід (фізичні одиниці)
    float ref[kNumOutputs];            // вихід ОРИГІНАЛЬНОЇ float-моделі (з Python)
    int   true_label;                  // правильний клас, або -1 якщо невідомий
};

// argmax: індекс найбільшого виходу — клас-переможець.
static int winner(const float* v, int n) {
    int best = 0;
    for (int i = 1; i < n; ++i) if (v[i] > v[best]) best = i;
    return best;
}
