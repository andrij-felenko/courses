/* =========================================================================
 * 1. Класичний підхід (AoS / Pointer Soup)
 * ========================================================================= */
typedef struct EntityClassic {
    float x, y, z;
    float vx, vy, vz;
    char  name[32];
    int   health;
} EntityClassic;

void update_classic(EntityClassic** entities, uint32_t count, float dt) {
    for (uint32_t i = 0; i < count; ++i) {
        EntityClassic* e = entities[i]; // Непрямий перехід за покажчиком (промах кешу)
        e->x += e->vx * dt;
        e->y += e->vy * dt;
        e->z += e->vz * dt;
    }
}

/* =========================================================================
 * 2. Data-Oriented Design (SoA / Лінійний потік)
 * ========================================================================= */
typedef struct {
    float* restrict x;
    float* restrict y;
    float* restrict z;
    const float* restrict vx;
    const float* restrict vy;
    const float* restrict vz;
} PositionStreamDOD;

void update_dod(PositionStreamDOD stream, uint32_t count, float dt) {
    /* Компілятор автоматично генерує SIMD-інструкції (AVX2 / NEON) */
    #pragma omp simd
    for (uint32_t i = 0; i < count; ++i) {
        stream.x[i] += stream.vx[i] * dt;
        stream.y[i] += stream.vy[i] * dt;
        stream.z[i] += stream.vz[i] * dt;
    }
}
