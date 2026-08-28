#ifndef DINIC_FLOW_H
#define DINIC_FLOW_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DINIC_SUCCESS = 0,
    DINIC_ERR_INVALID_VERTEX = 1,
    DINIC_ERR_NEGATIVE_CAPACITY = 2,
    DINIC_ERR_SAME_SOURCE_SINK = 3,
    DINIC_ERR_OVERFLOW = 4
} DinicStatus;

typedef struct {
    int32_t from;
    int32_t to;
    int64_t capacity;
    int64_t flow;
    uint32_t id;
} CDinicEdgeInfo;

typedef struct CDinicSolver CDinicSolver;

// Створення екземпляра розв'язувача
CDinicSolver* dinic_create(int32_t num_vertices);

// Звільнення пам'яті
void dinic_destroy(CDinicSolver* solver);

// Додавання ребра (повертає ідентифікатор ребра або UINT32_MAX при помилці)
uint32_t dinic_add_edge(CDinicSolver* solver, int32_t from, int32_t to, int64_t cap, int64_t rev_cap);

// Знаходження максимального потоку
int64_t dinic_solve(CDinicSolver* solver, int32_t source, int32_t sink, DinicStatus* status);

// Отримання потоку через ребро
int64_t dinic_get_flow(const CDinicSolver* solver, uint32_t edge_id);

// Отримання інформації про ребро
bool dinic_get_edge_info(const CDinicSolver* solver, uint32_t edge_id, CDinicEdgeInfo* out_info);

// Виділення мінімального розрізу (out_in_s повинен мати розмір num_vertices)
void dinic_extract_min_cut(const CDinicSolver* solver, int32_t source, bool* out_in_s);

// Скидання потоку
void dinic_reset_flow(CDinicSolver* solver);

#ifdef __cplusplus
}
#endif

#endif // DINIC_FLOW_H
