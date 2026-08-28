typedef struct {
    float x, y, z;
    float vx, vy, vz;
    float mass;
    float radius;
    int id;
    int flags;
    float pad[2]; // Доповнення до 64 байтів
} Particle;

Particle particles[1000000];
