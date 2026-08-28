#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Елемент ряду Проні (паралельна вітка Максвелла) */
typedef struct {
    double G_i;    /* Модуль зсуву i-ї вітки (Па) */
    double tau_i;  /* Час релаксації i-ї вітки (с) */
    double h_i;    /* Внутрішня змінна стану (внутрішнє напруження) */
} prony_element_t;

/* Структура узагальненої моделі Максвелла */
typedef struct {
    double G_inf;             /* Тривалий рівноважний модуль при t -> inf (Па) */
    size_t num_elements;      /* Кількість релаксаційних віток */
    prony_element_t *elements;/* Масив віток Проні */
} viscoelastic_model_t;

/* Результат обчислення динамічного модуля DMA */
typedef struct {
    double storage_modulus; /* G' (Па) */
    double loss_modulus;    /* G'' (Па) */
    double loss_tangent;    /* tan(delta) */
} dma_result_t;

/* Створення та ініціалізація моделі */
viscoelastic_model_t* viscoelastic_create(double G_inf, const double *G_i, const double *tau_i, size_t count) {
    viscoelastic_model_t *model = (viscoelastic_model_t*)malloc(sizeof(viscoelastic_model_t));
    if (!model) return NULL;

    model->G_inf = G_inf;
    model->num_elements = count;
    model->elements = (prony_element_t*)malloc(count * sizeof(prony_element_t));
    if (!model->elements) {
        free(model);
        return NULL;
    }

    for (size_t i = 0; i < count; ++i) {
        model->elements[i].G_i = G_i[i];
        model->elements[i].tau_i = tau_i[i];
        model->elements[i].h_i = 0.0;
    }

    return model;
}

/* Звільнення пам'яті */
void viscoelastic_free(viscoelastic_model_t *model) {
    if (model) {
        free(model->elements);
        free(model);
    }
}

/* Обчислення аналітичного модуля релаксації G(t) */
double viscoelastic_relaxation_modulus(const viscoelastic_model_t *model, double t) {
    double G_t = model->G_inf;
    for (size_t i = 0; i < model->num_elements; ++i) {
        G_t += model->elements[i].G_i * exp(-t / model->elements[i].tau_i);
    }
    return G_t;
}

/* Ресет внутрішніх змінних стану перед новим розрахунком */
void viscoelastic_reset_state(viscoelastic_model_t *model) {
    for (size_t i = 0; i < model->num_elements; ++i) {
        model->elements[i].h_i = 0.0;
    }
}

/* Оновлення стану моделі за крок часу dt при прирості деформації d_gamma */
double viscoelastic_step_strain(viscoelastic_model_t *model, double d_gamma, double dt) {
    double total_stress = model->G_inf * d_gamma;

    for (size_t i = 0; i < model->num_elements; ++i) {
        prony_element_t *e = &model->elements[i];
        /* Рекурентна експоненціальна схема інтегрування підкроку */
        double exp_factor = exp(-dt / e->tau_i);
        /* Оновлення внутрішньої змінної h_i */
        e->h_i = e->h_i * exp_factor + e->G_i * d_gamma * exp_factor;
        total_stress += e->h_i;
    }

    return total_stress;
}

/* Обчислення комплексно-динамічного модуля DMA при частоті omega (рад/с) */
dma_result_t viscoelastic_compute_dma(const viscoelastic_model_t *model, double omega) {
    dma_result_t res;
    res.storage_modulus = model->G_inf;
    res.loss_modulus = 0.0;

    for (size_t i = 0; i < model->num_elements; ++i) {
        double w_tau = omega * model->elements[i].tau_i;
        double w_tau_sq = w_tau * w_tau;
        double denom = 1.0 + w_tau_sq;

        res.storage_modulus += model->elements[i].G_i * (w_tau_sq / denom);
        res.loss_modulus    += model->elements[i].G_i * (w_tau / denom);
    }

    res.loss_tangent = (res.storage_modulus > 1e-12) ? (res.loss_modulus / res.storage_modulus) : 0.0;
    return res;
}

int main(void) {
    /* Параметри поліметилметакрилату (PMMA) при 23 °C */
    double G_inf = 1.2e8; /* 120 МПа тривалий модуль */
    double G_i[]   = {5.0e8, 3.0e8, 1.5e8}; /* Три вітки релаксації (Па) */
    double tau_i[] = {0.1,   1.0,   10.0};  /* Часи релаксації (с) */

    viscoelastic_model_t *model = viscoelastic_create(G_inf, G_i, tau_i, 3);
    if (!model) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    printf("=== 1. ТЕСТ РЕЛАКСАЦІЇ НАПРУЖЕНЬ (G(t)) ===\n");
    printf("Час t (с)    | Модуль G(t) (МПа) | Відносне спадання\n");
    printf("---------------------------------------------------\n");
    double G_0 = viscoelastic_relaxation_modulus(model, 0.0);
    for (double t = 0.0; t <= 20.0; t += 2.0) {
        double G_t = viscoelastic_relaxation_modulus(model, t);
        printf("%10.2f   | %17.2f | %17.2f%%\n", t, G_t / 1.0e6, (G_t / G_0) * 100.0);
    }

    printf("\n=== 2. ТЕСТ ДИНАМІЧНОГО МЕХАНІЧНОГО АНАЛІЗУ (DMA) ===\n");
    printf("Частота w (рад/с) | G' (МПа)    | G'' (МПа)   | tan(delta)\n");
    printf("-----------------------------------------------------------\n");
    double freqs[] = {0.01, 0.1, 1.0, 10.0, 100.0};
    for (size_t i = 0; i < sizeof(freqs)/sizeof(freqs[0]); ++i) {
        dma_result_t dma = viscoelastic_compute_dma(model, freqs[i]);
        printf("%17.2f | %11.2f | %11.2f | %10.4f\n",
               freqs[i], dma.storage_modulus / 1.0e6, dma.loss_modulus / 1.0e6, dma.loss_tangent);
    }

    viscoelastic_free(model);
    return 0;
}
