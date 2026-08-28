#include <stdlib.h>
#include <stdio.h>
#include <math.h>

typedef struct {
    float x, y, z;
    float vx, vy, vz;
    float mass;
    float radius;
    int id;
    int flags;
    float pad[2]; // Доповнення структури до 48 байтів
} ParticleAoS;

void update_particles_aos(ParticleAoS *restrict p, int n, float dt, float damping, float min_b, float max_b)
{
    for (int i = 0; i < n; i++) {
        float vx = p[i].vx * damping;
        float vy = p[i].vy * damping;
        float vz = p[i].vz * damping;

        p[i].vx = vx;
        p[i].vy = vy;
        p[i].vz = vz;

        float x = p[i].x + vx * dt;
        float y = p[i].y + vy * dt;
        float z = p[i].z + vz * dt;

        p[i].x = (x < min_b) ? min_b : (x > max_b ? max_b : x);
        p[i].y = (y < min_b) ? min_b : (y > max_b ? max_b : y);
        p[i].z = (z < min_b) ? min_b : (z > max_b ? max_b : z);
    }
}
