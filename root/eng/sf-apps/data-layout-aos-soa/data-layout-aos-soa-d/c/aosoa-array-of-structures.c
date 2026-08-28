#define LANES 8

typedef struct {
    float x[LANES];
    float y[LANES];
    float z[LANES];
    float vx[LANES];
    float vy[LANES];
    float vz[LANES];
} ParticleTile;

ParticleTile tiles[1000000 / LANES];
