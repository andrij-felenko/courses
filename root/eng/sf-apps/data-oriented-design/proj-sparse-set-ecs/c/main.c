#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define INVALID_INDEX UINT32_MAX

typedef uint32_t Entity;

typedef struct {
    float x;
    float y;
    float z;
} Position;

typedef struct {
    float vx;
    float vy;
    float vz;
} Velocity;

/* Сховище компонентів Position та Velocity на базі Sparse Set */
typedef struct {
    uint32_t* sparse;
    uint32_t  sparse_capacity;
    
    Entity*   dense_entities;
    Position* dense_pos;
    Velocity* dense_vel;
    uint32_t  count;
    uint32_t  dense_capacity;
} PositionPool;

bool pool_init(PositionPool* pool, uint32_t max_entities, uint32_t initial_capacity) {
    pool->sparse = (uint32_t*)malloc(sizeof(uint32_t) * max_entities);
    if (!pool->sparse) return false;
    
    for (uint32_t i = 0; i < max_entities; ++i) {
        pool->sparse[i] = INVALID_INDEX;
    }
    pool->sparse_capacity = max_entities;

    pool->dense_entities = (Entity*)malloc(sizeof(Entity) * initial_capacity);
    pool->dense_pos      = (Position*)malloc(sizeof(Position) * initial_capacity);
    pool->dense_vel      = (Velocity*)malloc(sizeof(Velocity) * initial_capacity);
    
    if (!pool->dense_entities || !pool->dense_pos || !pool->dense_vel) {
        free(pool->sparse);
        free(pool->dense_entities);
        free(pool->dense_pos);
        free(pool->dense_vel);
        return false;
    }

    pool->count = 0;
    pool->dense_capacity = initial_capacity;
    return true;
}

void pool_free(PositionPool* pool) {
    free(pool->sparse);
    free(pool->dense_entities);
    free(pool->dense_pos);
    free(pool->dense_vel);
    memset(pool, 0, sizeof(PositionPool));
}

bool pool_has(const PositionPool* pool, Entity e) {
    if (e >= pool->sparse_capacity) return false;
    return pool->sparse[e] != INVALID_INDEX;
}

bool pool_add(PositionPool* pool, Entity e, Position pos, Velocity vel) {
    if (e >= pool->sparse_capacity) return false;
    if (pool_has(pool, e)) return false;

    if (pool->count >= pool->dense_capacity) {
        uint32_t new_cap = pool->dense_capacity * 2;
        Entity* new_ent   = (Entity*)realloc(pool->dense_entities, sizeof(Entity) * new_cap);
        Position* new_pos = (Position*)realloc(pool->dense_pos, sizeof(Position) * new_cap);
        Velocity* new_vel = (Velocity*)realloc(pool->dense_vel, sizeof(Velocity) * new_cap);
        if (!new_ent || !new_pos || !new_vel) return false;
        
        pool->dense_entities = new_ent;
        pool->dense_pos      = new_pos;
        pool->dense_vel      = new_vel;
        pool->dense_capacity = new_cap;
    }

    uint32_t idx = pool->count;
    pool->dense_entities[idx] = e;
    pool->dense_pos[idx]      = pos;
    pool->dense_vel[idx]      = vel;
    pool->sparse[e]           = idx;
    pool->count++;
    return true;
}

bool pool_remove(PositionPool* pool, Entity e) {
    if (!pool_has(pool, e)) return false;

    uint32_t removed_idx = pool->sparse[e];
    uint32_t last_idx    = pool->count - 1;

    if (removed_idx != last_idx) {
        Entity last_entity = pool->dense_entities[last_idx];
        
        /* Копіюємо останній елемент на місце видаленого */
        pool->dense_entities[removed_idx] = last_entity;
        pool->dense_pos[removed_idx]      = pool->dense_pos[last_idx];
        pool->dense_vel[removed_idx]      = pool->dense_vel[last_idx];

        /* Оновлюємо розріджений індекс перенесеної сутності */
        pool->sparse[last_entity] = removed_idx;
    }

    pool->sparse[e] = INVALID_INDEX;
    pool->count--;
    return true;
}

/* Система фізики: суто лінійна обробка суміжних буферів */
void movement_system(PositionPool* pool, float dt) {
    Position* restrict pos = pool->dense_pos;
    const Velocity* restrict vel = pool->dense_vel;
    const uint32_t count = pool->count;

    #pragma omp simd
    for (uint32_t i = 0; i < count; ++i) {
        pos[i].x += vel[i].vx * dt;
        pos[i].y += vel[i].vy * dt;
        pos[i].z += vel[i].vz * dt;
    }
}
