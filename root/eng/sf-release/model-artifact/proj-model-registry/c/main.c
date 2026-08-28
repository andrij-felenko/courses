#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <unistd.h>

// Імітація обчислення контрольної суми
uint64_t compute_hash_c(const uint8_t* data, size_t len) {
    uint64_t hash = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        hash = (hash ^ data[i]) * 1099511628211ULL;
    }
    return hash;
}

// Структура моделі з лічильником посилань для безпечного видалення (RCU-патерн)
typedef struct ModelInstanceC {
    char name[64];
    char version[32];
    uint64_t checksum;
    size_t input_dim;
    size_t output_dim;
    float* weights;
    atomic_int ref_count; // Лічильник активних потоків інференсу
} ModelInstanceC;

// Менеджер моделі
typedef struct ModelRuntimeManagerC {
    _Atomic(ModelInstanceC*) active_model;
    pthread_mutex_t reload_mutex;
} ModelRuntimeManagerC;

// Створення екземпляра
ModelInstanceC* model_instance_create(const char* name, const char* version, 
                                      uint64_t checksum, size_t in_dim, size_t out_dim) {
    ModelInstanceC* m = (ModelInstanceC*)malloc(sizeof(ModelInstanceC));
    if (!m) return NULL;

    strncpy(m->name, name, sizeof(m->name) - 1);
    strncpy(m->version, version, sizeof(m->version) - 1);
    m->checksum = checksum;
    m->input_dim = in_dim;
    m->output_dim = out_dim;
    m->weights = (float*)malloc(in_dim * out_dim * sizeof(float));
    if (!m->weights) {
        free(m);
        return NULL;
    }
    for (size_t i = 0; i < in_dim * out_dim; ++i) {
        m->weights[i] = 0.05f;
    }
    atomic_init(&m->ref_count, 1); // 1 посилання утримує менеджер
    return m;
}

// Звільнення пам'яті моделі, коли ref_count падає до 0
void model_instance_release(ModelInstanceC* m) {
    if (!m) return;
    if (atomic_fetch_sub(&m->ref_count, 1) == 1) {
        free(m->weights);
        free(m);
    }
}

void model_manager_init(ModelRuntimeManagerC* mgr) {
    atomic_init(&mgr->active_model, NULL);
    pthread_mutex_init(&mgr->reload_mutex, NULL);
}

// Гаряче атомарне оновлення артефакту
bool model_manager_load(ModelRuntimeManagerC* mgr, const char* name, 
                        const char* version, uint64_t expected_hash, 
                        size_t in_dim, size_t out_dim, 
                        const uint8_t* raw_bytes, size_t byte_len) {
    // 1. Верифікація цілісності
    uint64_t actual_hash = compute_hash_c(raw_bytes, byte_len);
    if (actual_hash != expected_hash) {
        fprintf(stderr, "[Security Alert] Невідповідність хешу в C-рушії!\n");
        return false;
    }

    // 2. Створення нового екземпляра
    ModelInstanceC* new_model = model_instance_create(name, version, actual_hash, in_dim, out_dim);
    if (!new_model) return false;

    // 3. Атомарна заміна покажчика з пам'яттю Release
    pthread_mutex_lock(&mgr->reload_mutex);
    ModelInstanceC* old_model = atomic_exchange_explicit(&mgr->active_model, new_model, memory_order_release);
    pthread_mutex_unlock(&mgr->reload_mutex);

    // 4. Декремент лічильника старої моделі (буде звільнена, коли воркери завершать роботу)
    if (old_model) {
        model_instance_release(old_model);
    }

    printf("[C MLOps] Успішно активовано версію %s\n", version);
    return true;
}

// Виконання передбачення
bool model_manager_predict(ModelRuntimeManagerC* mgr, const float* input, size_t in_len, 
                           float* output, size_t out_len) {
    // Атомарно отримуємо покажчик з семантикою Acquire
    ModelInstanceC* m = atomic_load_explicit(&mgr->active_model, memory_order_acquire);
    if (!m) return false;

    // Збільшуємо лічильник посилань, щоб модель не видалили під час розрахунку
    atomic_fetch_add(&m->ref_count, 1);

    // Перевірка розмірностей
    if (in_len != m->input_dim || out_len != m->output_dim) {
        model_instance_release(m);
        return false;
    }

    // Розрахунок прямого проходу
    for (size_t o = 0; o < m->output_dim; ++o) {
        float sum = 0.0f;
        for (size_t i = 0; i < m->input_dim; ++i) {
            sum += input[i] * m->weights[o * m->input_dim + i];
        }
        output[o] = 1.0f / (1.0f + expf(-sum));
    }

    // Звільняємо тимчасове посилання
    model_instance_release(m);
    return true;
}

void model_manager_destroy(ModelRuntimeManagerC* mgr) {
    ModelInstanceC* m = atomic_load_explicit(&mgr->active_model, memory_order_relaxed);
    if (m) {
        model_instance_release(m);
    }
    pthread_mutex_destroy(&mgr->reload_mutex);
}

int main() {
    ModelRuntimeManagerC manager;
    model_manager_init(&manager);

    uint8_t v1_data[] = {1, 2, 3, 4};
    uint64_t v1_hash = compute_hash_c(v1_data, sizeof(v1_data));

    if (!model_manager_load(&manager, "risk-c", "v1.0", v1_hash, 4, 1, v1_data, sizeof(v1_data))) {
        fprintf(stderr, "Помилка завантаження моделі v1.0\n");
        return 1;
    }

    float in[4] = {0.1f, 0.2f, 0.3f, 0.4f};
    float out[1] = {0.0f};

    if (model_manager_predict(&manager, in, 4, out, 1)) {
        printf("Результат передбачення v1.0: %f\n", out[0]);
    }

    // Завантажуємо v2.0 на місці
    uint8_t v2_data[] = {5, 6, 7, 8, 9};
    uint64_t v2_hash = compute_hash_c(v2_data, sizeof(v2_data));
    model_manager_load(&manager, "risk-c", "v2.0", v2_hash, 4, 1, v2_data, sizeof(v2_data));

    if (model_manager_predict(&manager, in, 4, out, 1)) {
        printf("Результат передбачення v2.0: %f\n", out[0]);
    }

    model_manager_destroy(&manager);
    return 0;
}
