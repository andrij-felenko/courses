#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

struct reachability_engine {
    size_t vertices;
    size_t words_per_row;
    tc_mode_t mode;
    bool auto_reflexive;
    bool is_computed;
    bool is_frozen;
    uint64_t *bit_matrix;
};

tc_status_t tc_engine_create(const tc_config_t *config, reachability_engine_t **out_engine) {
    if (!config || !out_engine) return TC_ERR_NULL_POINTER;
    if (config->vertices == 0) return TC_ERR_INVALID_VERTEX;

    reachability_engine_t *eng = (reachability_engine_t*)malloc(sizeof(reachability_engine_t));
    if (!eng) return TC_ERR_NO_MEMORY;

    eng->vertices = config->vertices;
    eng->words_per_row = (config->vertices + 63) / 64;
    eng->mode = config->mode;
    eng->auto_reflexive = config->auto_reflexive;
    eng->is_computed = false;
    eng->is_frozen = false;

    size_t total_words = eng->vertices * eng->words_per_row;
    eng->bit_matrix = (uint64_t*)calloc(total_words, sizeof(uint64_t));
    if (!eng->bit_matrix) {
        free(eng);
        return TC_ERR_NO_MEMORY;
    }

    if (eng->auto_reflexive) {
        for (size_t i = 0; i < eng->vertices; ++i) {
            size_t word_idx = i * eng->words_per_row + (i / 64);
            eng->bit_matrix[word_idx] |= (1ULL << (i % 64));
        }
    }

    *out_engine = eng;
    return TC_SUCCESS;
}

void tc_engine_destroy(reachability_engine_t *engine) {
    if (!engine) return;
    free(engine->bit_matrix);
    free(engine);
}

tc_status_t tc_add_edge(reachability_engine_t *engine, size_t u, size_t v) {
    if (!engine) return TC_ERR_NULL_POINTER;
    if (u >= engine->vertices || v >= engine->vertices) return TC_ERR_INVALID_VERTEX;
    if (engine->is_frozen) return TC_ERR_FROZEN;

    size_t word_idx = u * engine->words_per_row + (v / 64);
    engine->bit_matrix[word_idx] |= (1ULL << (v % 64));
    return TC_SUCCESS;
}

tc_status_t tc_compute(reachability_engine_t *engine) {
    if (!engine) return TC_ERR_NULL_POINTER;
    const size_t v = engine->vertices;
    const size_t wpr = engine->words_per_row;
    uint64_t *m = engine->bit_matrix;

    for (size_t k = 0; k < v; ++k) {
        size_t k_word = k / 64;
        uint64_t k_mask = (1ULL << (k % 64));

        for (size_t i = 0; i < v; ++i) {
            if ((m[i * wpr + k_word] & k_mask) != 0) {
                uint64_t *row_i = &m[i * wpr];
                const uint64_t *row_k = &m[k * wpr];
                for (size_t w = 0; w < wpr; ++w) {
                    row_i[w] |= row_k[w];
                }
            }
        }
    }

    engine->is_computed = true;
    engine->is_frozen = true;
    return TC_SUCCESS;
}

tc_status_t tc_is_reachable(const reachability_engine_t *engine, size_t u, size_t v, bool *out_reachable) {
    if (!engine || !out_reachable) return TC_ERR_NULL_POINTER;
    if (u >= engine->vertices || v >= engine->vertices) return TC_ERR_INVALID_VERTEX;
    if (!engine->is_computed) return TC_ERR_NOT_COMPUTED;

    size_t word_idx = u * engine->words_per_row + (v / 64);
    *out_reachable = (engine->bit_matrix[word_idx] & (1ULL << (v % 64))) != 0;
    return TC_SUCCESS;
}

tc_status_t tc_get_reachable_set(const reachability_engine_t *engine, size_t u, size_t **out_vertices, size_t *out_count) {
    if (!engine || !out_vertices || !out_count) return TC_ERR_NULL_POINTER;
    if (u >= engine->vertices) return TC_ERR_INVALID_VERTEX;
    if (!engine->is_computed) return TC_ERR_NOT_COMPUTED;

    size_t wpr = engine->words_per_row;
    const uint64_t *row_u = &engine->bit_matrix[u * wpr];

    size_t count = 0;
    for (size_t v = 0; v < engine->vertices; ++v) {
        if ((row_u[v / 64] & (1ULL << (v % 64))) != 0) {
            count++;
        }
    }

    size_t *res = (size_t*)malloc(count * sizeof(size_t));
    if (!res && count > 0) return TC_ERR_NO_MEMORY;

    size_t idx = 0;
    for (size_t v = 0; v < engine->vertices; ++v) {
        if ((row_u[v / 64] & (1ULL << (v % 64))) != 0) {
            res[idx++] = v;
        }
    }

    *out_vertices = res;
    *out_count = count;
    return TC_SUCCESS;
}
