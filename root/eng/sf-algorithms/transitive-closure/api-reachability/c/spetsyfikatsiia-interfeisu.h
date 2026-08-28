#ifndef REACHABILITY_H
#define REACHABILITY_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#define REACHABILITY_API_VERSION_MAJOR 1
#define REACHABILITY_API_VERSION_MINOR 0

typedef enum {
    TC_SUCCESS            =  0,
    TC_ERR_NULL_POINTER   = -1,
    TC_ERR_INVALID_VERTEX = -2,
    TC_ERR_NO_MEMORY      = -3,
    TC_ERR_FROZEN         = -4,
    TC_ERR_NOT_COMPUTED   = -5
} tc_status_t;

typedef enum {
    TC_MODE_WARSHALL_SCALAR  = 0,
    TC_MODE_WARSHALL_BITSET  = 1,
    TC_MODE_SPARSE_DFS       = 2
} tc_mode_t;

typedef struct {
    size_t vertices;
    tc_mode_t mode;
    bool auto_reflexive;
} tc_config_t;

typedef struct reachability_engine reachability_engine_t;

#ifdef __cplusplus
extern "C" {
#endif

tc_status_t tc_engine_create(const tc_config_t *config, reachability_engine_t **out_engine);
void tc_engine_destroy(reachability_engine_t *engine);
tc_status_t tc_add_edge(reachability_engine_t *engine, size_t u, size_t v);
tc_status_t tc_compute(reachability_engine_t *engine);
tc_status_t tc_is_reachable(const reachability_engine_t *engine, size_t u, size_t v, bool *out_reachable);
tc_status_t tc_get_reachable_set(const reachability_engine_t *engine, size_t u, size_t *out_vertices, size_t *out_count);

#ifdef __cplusplus
}
#endif

#endif // REACHABILITY_H
