#include <math.h>
#include <stdint.h>

#define N 6        // скільки мічених прикладів у пам'яті
#define K 3        // скільки сусідів опитуємо

typedef struct { float temp, vib; int label; } Sample;  // label: 0 = норма, 1 = тривога

// Навчальний набір: пари ознак + правильна мітка («учитель» їх підписав)
static const Sample train[N] = {
    { 40.0f, 0.2f, 0 }, { 42.0f, 0.3f, 0 }, { 39.0f, 0.25f, 0 },  // спокійні
    { 85.0f, 1.8f, 1 }, { 88.0f, 2.1f, 1 }, { 90.0f, 1.9f, 1 },   // тривожні
};

// Квадрат відстані між входом і прикладом (корінь брати не треба — порядок той самий)
static float dist2(float t, float v, const Sample *s) {
    float dt = t - s->temp, dv = v - s->vib;
    return dt * dt + dv * dv;
}

// Класифікація нового входу (t, v) голосуванням K найближчих сусідів
int knn_classify(float t, float v) {
    int   idx[K];                 // індекси поточних K найближчих
    float best[K];                // їхні квадрати відстаней
    for (int j = 0; j < K; j++) { best[j] = INFINITY; idx[j] = -1; }

    for (int i = 0; i < N; i++) {          // пройти всі приклади
        float d = dist2(t, v, &train[i]);
        // якщо ближче за найдальшого з поточних K — вставити на його місце
        int worst = 0;
        for (int j = 1; j < K; j++)
            if (best[j] > best[worst]) worst = j;
        if (d < best[worst]) { best[worst] = d; idx[worst] = i; }
    }

    int votes = 0;                          // сума міток сусідів (0 або 1)
    for (int j = 0; j < K; j++)
        votes += train[idx[j]].label;
    return (votes * 2 > K) ? 1 : 0;         // більшість голосів → клас
}
