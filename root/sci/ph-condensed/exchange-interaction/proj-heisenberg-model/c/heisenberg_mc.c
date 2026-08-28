/* heisenberg_mc.c — Моделювання 2D спинової решітки Гейзенберга на мові C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    int size;
    double J;
    double h;
    double temp;
    Vec3 *spins;
} Lattice;

static double rand_double(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

static Vec3 random_unit_vector(void) {
    double z = 2.0 * rand_double() - 1.0;
    double phi = 2.0 * M_PI * rand_double();
    double r = sqrt(1.0 - z * z);
    Vec3 v = { r * cos(phi), r * sin(phi), z };
    return v;
}

static double dot_product(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

Lattice* lattice_create(int size, double J, double h, double temp) {
    Lattice *lat = (Lattice*)malloc(sizeof(Lattice));
    lat->size = size;
    lat->J = J;
    lat->h = h;
    lat->temp = temp;
    lat->spins = (Vec3*)malloc(sizeof(Vec3) * size * size);

    for (int i = 0; i < size * size; ++i) {
        lat->spins[i] = random_unit_vector();
    }
    return lat;
}

void lattice_free(Lattice *lat) {
    if (lat) {
        free(lat->spins);
        free(lat);
    }
}

static void get_neighbors(int idx, int size, int nbrs[4]) {
    int r = idx / size;
    int c = idx % size;
    nbrs[0] = ((r - 1 + size) % size) * size + c; /* Північ */
    nbrs[1] = ((r + 1) % size) * size + c;        /* Південь */
    nbrs[2] = r * size + ((c + 1) % size);        /* Схід */
    nbrs[3] = r * size + ((c - 1 + size) % size); /* Захід */
}

void metropolis_step(Lattice *lat) {
    int total_sites = lat->size * lat->size;
    for (int step = 0; step < total_sites; ++step) {
        int idx = rand() % total_sites;
        int nbrs[4];
        get_neighbors(idx, lat->size, nbrs);

        Vec3 old_spin = lat->spins[idx];
        Vec3 new_spin = random_unit_vector();

        Vec3 sum_nbrs = {0.0, 0.0, 0.0};
        for (int k = 0; k < 4; ++k) {
            sum_nbrs.x += lat->spins[nbrs[k]].x;
            sum_nbrs.y += lat->spins[nbrs[k]].y;
            sum_nbrs.z += lat->spins[nbrs[k]].z;
        }

        double dE = -lat->J * (dot_product(new_spin, sum_nbrs) - dot_product(old_spin, sum_nbrs))
                    - lat->h * (new_spin.z - old_spin.z);

        if (dE <= 0.0 || rand_double() < exp(-dE / lat->temp)) {
            lat->spins[idx] = new_spin;
        }
    }
}

void compute_observables(const Lattice *lat, double *energy, double *magnetization) {
    double total_E = 0.0;
    Vec3 total_M = {0.0, 0.0, 0.0};
    int size = lat->size;

    for (int idx = 0; idx < size * size; ++idx) {
        int nbrs[4];
        get_neighbors(idx, size, nbrs);
        
        /* Враховуємо лише вихідні зв'язки Схід і Південь, щоб не подвоювати */
        double e_pair = dot_product(lat->spins[idx], lat->spins[nbrs[1]]) +
                        dot_product(lat->spins[idx], lat->spins[nbrs[2]]);
        
        total_E -= lat->J * e_pair + lat->h * lat->spins[idx].z;
        total_M.x += lat->spins[idx].x;
        total_M.y += lat->spins[idx].y;
        total_M.z += lat->spins[idx].z;
    }

    int n_sites = size * size;
    *energy = total_E / n_sites;
    *magnetization = sqrt(dot_product(total_M, total_M)) / n_sites;
}

int main(void) {
    srand((unsigned int)time(NULL));
    int size = 16;
    double J = 1.0;
    double h = 0.05;
    double temp = 0.8;

    Lattice *lat = lattice_create(size, J, h, temp);

    printf("Термалізація 2D решітки Гейзенберга (%dx%d)...\n", size, size);
    for (int i = 0; i < 2000; ++i) {
        metropolis_step(lat);
    }

    printf("Вимірювання термодинамічних величин...\n");
    double avg_E = 0.0, avg_M = 0.0;
    int samples = 1000;
    for (int i = 0; i < samples; ++i) {
        metropolis_step(lat);
        double E, M;
        compute_observables(lat, &E, &M);
        avg_E += E;
        avg_M += M;
    }

    printf("Результати (T = %.2f, h = %.2f):\n", temp, h);
    printf(" Середня енергія на вузол: %f\n", avg_E / samples);
    printf(" Середня намагніченість |M|: %f\n", avg_M / samples);

    lattice_free(lat);
    return 0;
}
