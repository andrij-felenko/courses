#include <assert.h>
#include <stdlib.h>

// Проганяє один шар обома шляхами по T колонках і звіряє ОСТАННЮ вихідну колонку.
static bool equiv_check_layer(ConvLayer *L, int T) {
    int8_t in[64][CIN_MAX];
    int8_t out_batch[64][COUT_MAX];
    // 1. Синтетичне вікно з ВІДОМИМ, несиметричним у часі візерунком —
    //    щоб будь-яке прокручення чи дзеркалення часу одразу проступило.
    for (int t = 0; t < T; t++)
        for (int c = 0; c < L->cin; c++)
            in[t][c] = (int8_t)(((t * 7 + c * 3) % 255) - 128);

    // 2. Еталон: разова згортка по всьому вікну.
    conv_batch(L, T, in, out_batch);

    // 3. Потік: скидаємо стан і згодовуємо ті самі колонки по одній.
    L->w_head = 0; L->filled = 0;
    int8_t last_stream[COUT_MAX]; bool have = false;
    for (int t = 0; t < T; t++)
        have = conv_step(L, in[t], last_stream);   // остання успішна = найновіша

    if (!have) return false;                        // вікно коротше за прогрів — не тест
    // 4. Найновіша колонка потоку МУСИТЬ збігтися з останньою колонкою еталону — до біта.
    for (int oc = 0; oc < L->cout; oc++)
        if (last_stream[oc] != out_batch[T - 1][oc]) {
            // рівно тут проступає перекручення по head, зсув часу чи хиба обрізання
            return false;
        }
    return true;
}
