# ⚙️ Практична реалізація LSH-індексу

Ця вставка містить повну практичну реалізацію індексу хешування з урахуванням локальності (Locality-Sensitive Hashing) мовами C та C++. Реалізація базується на алгоритмі SimHash (випадкові гіперплощини для косинусної відстані) та підсиленні смугами (Banding), що дає змогу ефективно шукати найближчі вектори у високовимірному просторі.

## Опис структури реалізації

Індекс LSH складається з трьох ключових компонентів:
1. **Генератор гіперплощин**: створює `M = k · L` випадкових нормальних векторів `r ~ N(0, I)`.
2. **Модуль смугового хешування (Banding)**: кодує `k` бітів кожної смуги у 64-бітне значення бакету.
3. **Хеш-таблиці бакетів**: `L` окремих хеш-таблиць, кожна з яких зберігає список ідентифікаторів векторів, що потрапили у відповідні комірки.

При запиті вектор опитує всі `L` хеш-таблиць, формує унікальну множину кандидатів і виконує точний перерахунок косинусної відстані лише для відібраних об'єктів.

```
:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define M_PI_VAL 3.14159265358979323846

/* --- Структура вектора даних --- */
typedef struct {
    uint64_t id;
    float *data;
    size_t dim;
} vector_t;

/* --- Результат пошуку сусіда --- */
typedef struct {
    uint64_t id;
    float distance;
} neighbor_result_t;

/* --- Вузол однозв'язного списку бакета --- */
typedef struct bucket_node {
    uint64_t vector_id;
    struct bucket_node *next;
} bucket_node_t;

/* --- Хеш-таблиця для однієї смуги --- */
typedef struct {
    size_t capacity;
    bucket_node_t **buckets;
} band_table_t;

/* --- Головна структура LSH-індексу --- */
typedef struct {
    size_t dim;             /* вимірність векторів */
    size_t k;               /* кількість гіперплощин на смугу */
    size_t num_bands;       /* кількість смуг L */
    size_t total_hyperplanes; /* total = k * num_bands */
    float *hyperplanes;     /* плоский масив гіперплощин [total * dim] */
    band_table_t *tables;   /* масив з L хеш-таблиць */
    
    /* Збереження векторів для підсумкового реранкінгу */
    vector_t *stored_vectors;
    size_t num_vectors;
    size_t capacity_vectors;
} lsh_index_t;

/* Генерація стандартного нормального числа за Box-Muller */
static float rand_normal(void) {
    float u1 = (float)rand() / (float)RAND_MAX;
    float u2 = (float)rand() / (float)RAND_MAX;
    if (u1 < 1e-7f) u1 = 1e-7f;
    return sqrtf(-2.0f * logf(u1)) * cosf(2.0f * (float)M_PI_VAL * u2);
}

/* Обчислення косинусної відстані: 1.0 - cos(u, v) */
static float cosine_distance(const float *u, const float *v, size_t dim) {
    float dot = 0.0f, norm_u = 0.0f, norm_v = 0.0f;
    for (size_t i = 0; i < dim; ++i) {
        dot += u[i] * v[i];
        norm_u += u[i] * u[i];
        norm_v += v[i] * v[i];
    }
    if (norm_u <= 1e-9f || norm_v <= 1e-9f) return 1.0f;
    float sim = dot / (sqrtf(norm_u) * sqrtf(norm_v));
    if (sim > 1.0f) sim = 1.0f;
    if (sim < -1.0f) sim = -1.0f;
    return 1.0f - sim;
}

/* Створення LSH індексу */
lsh_index_t *lsh_create(size_t dim, size_t k, size_t num_bands, size_t bucket_capacity) {
    lsh_index_t *idx = (lsh_index_t *)calloc(1, sizeof(lsh_index_t));
    if (!idx) return NULL;

    idx->dim = dim;
    idx->k = k;
    idx->num_bands = num_bands;
    idx->total_hyperplanes = k * num_bands;

    /* Ініціалізація гіперплощин */
    idx->hyperplanes = (float *)malloc(idx->total_hyperplanes * dim * sizeof(float));
    for (size_t i = 0; i < idx->total_hyperplanes * dim; ++i) {
        idx->hyperplanes[i] = rand_normal();
    }

    /* Створення L хеш-таблиць */
    idx->tables = (band_table_t *)malloc(num_bands * sizeof(band_table_t));
    for (size_t b = 0; b < num_bands; ++b) {
        idx->tables[b].capacity = bucket_capacity;
        idx->tables[b].buckets = (bucket_node_t **)calloc(bucket_capacity, sizeof(bucket_node_t *));
    }

    idx->capacity_vectors = 16;
    idx->stored_vectors = (vector_t *)malloc(idx->capacity_vectors * sizeof(vector_t));
    idx->num_vectors = 0;

    return idx;
}

/* Обчислення хешу смуги для вектора */
static uint64_t compute_band_hash(const lsh_index_t *idx, const float *vec, size_t band_idx) {
    uint64_t band_code = 0;
    size_t hp_offset = band_idx * idx->k;

    for (size_t i = 0; i < idx->k; ++i) {
        const float *hp = &idx->hyperplanes[(hp_offset + i) * idx->dim];
        float dot = 0.0f;
        for (size_t d = 0; d < idx->dim; ++d) {
            dot += vec[d] * hp[d];
        }
        if (dot >= 0.0f) {
            band_code |= (1ULL << i);
        }
    }
    return band_code;
}

/* Вставка вектора в індекс */
bool lsh_insert(lsh_index_t *idx, uint64_t id, const float *vec_data) {
    /* Збереження копії вектора */
    if (idx->num_vectors >= idx->capacity_vectors) {
        size_t new_cap = idx->capacity_vectors * 2;
        vector_t *new_arr = (vector_t *)realloc(idx->stored_vectors, new_cap * sizeof(vector_t));
        if (!new_arr) return false;
        idx->stored_vectors = new_arr;
        idx->capacity_vectors = new_cap;
    }

    float *data_copy = (float *)malloc(idx->dim * sizeof(float));
    memcpy(data_copy, vec_data, idx->dim * sizeof(float));

    idx->stored_vectors[idx->num_vectors].id = id;
    idx->stored_vectors[idx->num_vectors].data = data_copy;
    idx->stored_vectors[idx->num_vectors].dim = idx->dim;
    idx->num_vectors++;

    /* Вставка ID у L хеш-таблиць */
    for (size_t b = 0; b < idx->num_bands; ++b) {
        uint64_t hash_val = compute_band_hash(idx, vec_data, b);
        size_t slot = hash_val % idx->tables[b].capacity;

        bucket_node_t *node = (bucket_node_t *)malloc(sizeof(bucket_node_t));
        node->vector_id = id;
        node->next = idx->tables[b].buckets[slot];
        idx->tables[b].buckets[slot] = node;
    }
    return true;
}

/* Допоміжна функція компаратора для qsort */
static int compare_neighbors(const void *a, const void *b) {
    float d1 = ((const neighbor_result_t *)a)->distance;
    float d2 = ((const neighbor_result_t *)b)->distance;
    if (d1 < d2) return -1;
    if (d1 > d2) return 1;
    return 0;
}

/* Пошук K найближчих сусідів */
size_t lsh_query(const lsh_index_t *idx, const float *query_vec, size_t top_k, neighbor_result_t *out_results) {
    bool *candidate_flags = (bool *)calloc(idx->num_vectors, sizeof(bool));
    size_t num_candidates = 0;

    /* Збір кандидатів з усіх L смуг */
    for (size_t b = 0; b < idx->num_bands; ++b) {
        uint64_t hash_val = compute_band_hash(idx, query_vec, b);
        size_t slot = hash_val % idx->tables[b].capacity;

        bucket_node_t *curr = idx->tables[b].buckets[slot];
        while (curr) {
            /* Знаходимо внутрішній індекс вектора */
            for (size_t v = 0; v < idx->num_vectors; ++v) {
                if (idx->stored_vectors[v].id == curr->vector_id) {
                    if (!candidate_flags[v]) {
                        candidate_flags[v] = true;
                        num_candidates++;
                    }
                    break;
                }
            }
            curr = curr->next;
        }
    }

    if (num_candidates == 0) {
        free(candidate_flags);
        return 0;
    }

    /* Обчислення точної косинусної відстані для кандидатів */
    neighbor_result_t *cand_arr = (neighbor_result_t *)malloc(num_candidates * sizeof(neighbor_result_t));
    size_t idx_c = 0;

    for (size_t v = 0; v < idx->num_vectors; ++v) {
        if (candidate_flags[v]) {
            cand_arr[idx_c].id = idx->stored_vectors[v].id;
            cand_arr[idx_c].distance = cosine_distance(query_vec, idx->stored_vectors[v].data, idx->dim);
            idx_c++;
        }
    }

    qsort(cand_arr, num_candidates, sizeof(neighbor_result_t), compare_neighbors);

    size_t return_count = (top_k < num_candidates) ? top_k : num_candidates;
    memcpy(out_results, cand_arr, return_count * sizeof(neighbor_result_t));

    free(cand_arr);
    free(candidate_flags);
    return return_count;
}

/* Звільнення ресурсів */
void lsh_destroy(lsh_index_t *idx) {
    if (!idx) return;
    for (size_t b = 0; b < idx->num_bands; ++b) {
        for (size_t c = 0; c < idx->tables[b].capacity; ++c) {
            bucket_node_t *curr = idx->tables[b].buckets[c];
            while (curr) {
                bucket_node_t *tmp = curr;
                curr = curr->next;
                free(tmp);
            }
        }
        free(idx->tables[b].buckets);
    }
    free(idx->tables);

    for (size_t v = 0; v < idx->num_vectors; ++v) {
        free(idx->stored_vectors[v].data);
    }
    free(idx->stored_vectors);
    free(idx->hyperplanes);
    free(idx);
}

int main(void) {
    srand(42);
    size_t dim = 4;
    size_t k = 3, num_bands = 5;

    lsh_index_t *index = lsh_create(dim, k, num_bands, 1024);

    float v1[4] = {1.0f, 2.0f, 3.0f, 0.0f};
    float v2[4] = {1.0f, 2.1f, 2.9f, 0.1f}; /* Схожий на v1 */
    float v3[4] = {-1.0f, -2.0f, -3.0f, 0.0f}; /* Протилежний */

    lsh_insert(index, 101, v1);
    lsh_insert(index, 102, v2);
    lsh_insert(index, 103, v3);

    float query[4] = {1.0f, 2.0f, 3.0f, 0.05f};
    neighbor_result_t results[5];
    size_t found = lsh_query(index, query, 2, results);

    printf("Знайдено кандидатів для запиту: %zu\n", found);
    for (size_t i = 0; i < found; ++i) {
        printf("  Top %zu: ID = %llu, Cosine Distance = %.4f\n", 
               i + 1, (unsigned long long)results[i].id, results[i].distance);
    }

    lsh_destroy(index);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <random>
#include <cmath>
#include <algorithm>
#include <memory>
#include <span >
#include <expected>

namespace lsh {

struct NeighborResult {
    uint64_t id;
    float distance;
};

class SimHashLSH {
public:
    SimHashLSH(size_t dim, size_t k, size_t num_bands)
        : dim_(dim), k_(k), num_bands_(num_bands), gen_(42) {
        
        std::normal_distribution<float> dist(0.0f, 1.0f);
        hyperplanes_.resize(num_bands_ * k_);
        
        for (auto& hp : hyperplanes_) {
            hp.resize(dim_);
            for (size_t d = 0; d < dim_; ++d) {
                hp[d] = dist(gen_);
            }
        }
        band_tables_.resize(num_bands_);
    }

    void insert(uint64_t id, std::span<const float> vec) {
        vectors_.push_back(VectorEntry{id, std::vector<float>(vec.begin(), vec.end())});
        size_t internal_idx = vectors_.size() - 1;

        for (size_t b = 0; b < num_bands_; ++b) {
            uint64_t hash_code = compute_band_hash(vec, b);
            band_tables_[b][hash_code].push_back(internal_idx);
        }
    }

    [[nodiscard]] std::vector<NeighborResult> query(std::span<const float> query_vec, size_t top_k) const {
        std::unordered_set<size_t> candidate_indices;

        for (size_t b = 0; b < num_bands_; ++b) {
            uint64_t hash_code = compute_band_hash(query_vec, b);
            auto it = band_tables_[b].find(hash_code);
            if (it != band_tables_[b].end()) {
                for (size_t idx : it->second) {
                    candidate_indices.insert(idx);
                }
            }
        }

        std::vector<NeighborResult> results;
        results.reserve(candidate_indices.size());

        for (size_t idx : candidate_indices) {
            const auto& entry = vectors_[idx];
            float dist = cosine_distance(query_vec, entry.data);
            results.push_back(NeighborResult{entry.id, dist});
        }

        std::sort(results.begin(), results.end(), [](const NeighborResult& a, const NeighborResult& b) {
            return a.distance < b.distance;
        });

        if (results.size() > top_k) {
            results.resize(top_k);
        }

        return results;
    }

private:
    struct VectorEntry {
        uint64_t id;
        std::vector<float> data;
    };

    uint64_t compute_band_hash(std::span<const float> vec, size_t band_idx) const {
        uint64_t code = 0;
        size_t hp_start = band_idx * k_;

        for (size_t i = 0; i < k_; ++i) {
            const auto& hp = hyperplanes_[hp_start + i];
            float dot = 0.0f;
            for (size_t d = 0; d < dim_; ++d) {
                dot += vec[d] * hp[d];
            }
            if (dot >= 0.0f) {
                code |= (1ULL << i);
            }
        }
        return code;
    }

    static float cosine_distance(std::span<const float> u, std::span<const float> v) {
        float dot = 0.0f, norm_u = 0.0f, norm_v = 0.0f;
        for (size_t i = 0; i < u.size(); ++i) {
            dot += u[i] * v[i];
            norm_u += u[i] * u[i];
            norm_v += v[i] * v[i];
        }
        if (norm_u <= 1e-9f || norm_v <= 1e-9f) return 1.0f;
        float sim = dot / (std::sqrt(norm_u) * std::sqrt(norm_v));
        return 1.0f - std::clamp(sim, -1.0f, 1.0f);
    }

    size_t dim_;
    size_t k_;
    size_t num_bands_;
    mutable std::mt19937 gen_;
    std::vector<std::vector<float>> hyperplanes_;
    std::vector<std::unordered_map<uint64_t, std::vector<size_t>>> band_tables_;
    std::vector<VectorEntry> vectors_;
};

} // namespace lsh

int main() {
    lsh::SimHashLSH index(4, 3, 5);

    std::vector<float> v1 = {1.0f, 2.0f, 3.0f, 0.0f};
    std::vector<float> v2 = {1.0f, 2.1f, 2.9f, 0.1f};
    std::vector<float> v3 = {-1.0f, -2.0f, -3.0f, 0.0f};

    index.insert(101, v1);
    index.insert(102, v2);
    index.insert(103, v3);

    std::vector<float> query = {1.0f, 2.0f, 3.0f, 0.05f};
    auto results = index.query(query, 2);

    std::cout << "Знайдено C++ кандидатів: " << results.size() << "\n";
    for (size_t i = 0; i < results.size(); ++i) {
        std::cout << "  Top " << i + 1 << ": ID = " << results[i].id 
                  << ", Cosine Distance = " << results[i].distance << "\n";
    }

    return 0;
}
```
:::

## Ключові аспекти оптимізації продуктивності

1. **Векторизація SIMD**: Обчислення скалярного добутку `dot += vec[d] * hp[d]` у гарячому циклі є ідеальним кандидатом для AVX-256 / AVX-512 FMA інструкцій (`_mm256_fmadd_ps`).
2. **Кешування пам'яті**: Замість використання `unordered_map` із вузловою структурою у продакшн-системах використовують плоскі хеш-таблиці з відкритою адресацією (Flat Hash Maps), що виключає Cache Miss при вибірці елементів смуги.
