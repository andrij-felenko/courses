/* Simulation of gas particle entropy evolution in C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define NUM_PARTICLES 10000
#define GRID_SIZE 20
#define TOTAL_CELLS (GRID_SIZE * GRID_SIZE)
#define TIME_STEPS 100

typedef struct {
    double x;
    double y;
} Particle;

/* Initialize particles in the left half of the box */
void init_particles(Particle *particles, int n) {
    for (int i = 0; i < n; i++) {
        particles[i].x = ((double)rand() / RAND_MAX) * (GRID_SIZE / 2.0);
        particles[i].y = ((double)rand() / RAND_MAX) * GRID_SIZE;
    }
}

/* Calculate normalized spatial entropy S / S_max */
double calculate_entropy(const Particle *particles, int n) {
    int counts[TOTAL_CELLS] = {0};

    for (int i = 0; i < n; i++) {
        int cx = (int)particles[i].x;
        int cy = (int)particles[i].y;
        if (cx < 0) cx = 0;
        if (cx >= GRID_SIZE) cx = GRID_SIZE - 1;
        if (cy < 0) cy = 0;
        if (cy >= GRID_SIZE) cy = GRID_SIZE - 1;

        int cell_idx = cy * GRID_SIZE + cx;
        counts[cell_idx]++;
    }

    double entropy = 0.0;
    for (int i = 0; i < TOTAL_CELLS; i++) {
        if (counts[i] > 0) {
            double p = (double)counts[i] / n;
            entropy -= p * log(p);
        }
    }

    double max_entropy = log(TOTAL_CELLS);
    return entropy / max_entropy;
}

/* Perform step with random thermal movement and wall reflections */
void update_positions(Particle *particles, int n, double step_size) {
    for (int i = 0; i < n; i++) {
        double dx = (((double)rand() / RAND_MAX) * 2.0 - 1.0) * step_size;
        double dy = (((double)rand() / RAND_MAX) * 2.0 - 1.0) * step_size;

        particles[i].x += dx;
        particles[i].y += dy;

        /* Boundary reflections */
        if (particles[i].x < 0.0) particles[i].x = -particles[i].x;
        if (particles[i].x >= GRID_SIZE) particles[i].x = 2.0 * GRID_SIZE - particles[i].x - 0.001;
        if (particles[i].y < 0.0) particles[i].y = -particles[i].y;
        if (particles[i].y >= GRID_SIZE) particles[i].y = 2.0 * GRID_SIZE - particles[i].y - 0.001;
    }
}

int main(void) {
    srand((unsigned int)time(NULL));

    Particle *particles = (Particle *)malloc(NUM_PARTICLES * sizeof(Particle));
    if (!particles) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    init_particles(particles, NUM_PARTICLES);

    printf("Step\tNormalized Entropy (S / S_max)\n");
    printf("---------------------------------------\n");

    for (int step = 0; step <= TIME_STEPS; step += 10) {
        double s = calculate_entropy(particles, NUM_PARTICLES);
        printf("%4d\t%.6f\n", step, s);
        
        for (int sub = 0; sub < 10; sub++) {
            update_positions(particles, NUM_PARTICLES, 0.5);
        }
    }

    free(particles);
    return 0;
}
