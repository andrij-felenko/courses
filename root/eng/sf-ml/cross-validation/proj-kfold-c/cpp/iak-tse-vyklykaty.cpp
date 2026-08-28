/* --- Твоя частина: одна модель, дві функції під контракт модуля. --- */

static Model g_model;                 /* стан однієї моделі (ваги тощо) */
extern Sample g_data[];               /* десь лежать самі приклади */

/* Навчити З НУЛЯ на прикладах, чиї індекси дав модуль.
   Ключове: обнулити модель на вході, бо той самий g_model
   використовується в наступному проході. */
void train(const int *idx, int n) {
    model_reset(&g_model);            /* СКИНУТИ — інакше ваги накопичаться між проходами */
    for (int i = 0; i < n; i++)
        model_update(&g_model, &g_data[idx[i]]);   /* учимо лише на цих прикладах */
}

/* Частка правильних на прикладах, чиї індекси дав модуль. */
float accuracy(const int *idx, int n) {
    int correct = 0;
    for (int i = 0; i < n; i++) {
        int pred = model_predict(&g_model, &g_data[idx[i]]);
        if (pred == g_data[idx[i]].label) correct++;
    }
    return (float)correct / (float)n;
}

/* --- Виклик: --- */
void run_evaluation(void) {
    cv_result r = cross_validate(200, 5, /*seed=*/42u);
    printf("точність: %.1f%% ± %.1f%%\n", r.mean * 100.0f, r.sd * 100.0f);
    /* напр.: "точність: 86.0% ± 1.7%" — середнє й розкид по 5 проходах */
}
