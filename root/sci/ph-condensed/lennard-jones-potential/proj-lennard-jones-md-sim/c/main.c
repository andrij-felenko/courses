#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N_PARTICLES 256
#define DT 0.005
#define N_STEPS 1000
#define RCUT 2.5
#define RSKIN 0.3
#define RLIST (RCUT + RSKIN)
#define RCUT2 (RCUT * RCUT)
#define RLIST2 (RLIST * RLIST)
#define TAU_TEMP 0.1

typedef struct {
    double x, y, z;
} Vector3;

typedef struct {
    Vector3 pos;
    Vector3 vel;
    Vector3 force;
    Vector3 last_pos;
} Particle;

typedef struct {
    int i, j;
} NeighborPair;

typedef struct {
    Particle *particles;
    NeighborPair *pairs;
    int n_particles;
    int n_pairs;
    int pairs_capacity;
    double box_len;
    double target_temp;
} LJSystem;

Vector3 min_image(Vector3 dr, double box_len) {
    double inv_b = 1.0 / box_len;
    Vector3 res;
    res.x = dr.x - box_len * round(dr.x * inv_b);
    res.y = dr.y - box_len * round(dr.y * inv_b);
    res.z = dr.z - box_len * round(dr.z * inv_b);
    return res;
}

void rebuild_neighbor_list(LJSystem *sys) {
    sys->n_pairs = 0;
    for (int i = 0; i < sys->n_particles - 1; i++) {
        for (int j = i + 1; j < sys->n_particles; j++) {
            Vector3 dr = {
                sys->particles[i].pos.x - sys->particles[j].pos.x,
                sys->particles[i].pos.y - sys->particles[j].pos.y,
                sys->particles[i].pos.z - sys->particles[j].pos.z
            };
            dr = min_image(dr, sys->box_len);
            double r2 = dr.x*dr.x + dr.y*dr.y + dr.z*dr.z;
            if (r2 < RLIST2) {
                if (sys->n_pairs >= sys->pairs_capacity) {
                    sys->pairs_capacity *= 2;
                    sys->pairs = (NeighborPair*)realloc(sys->pairs, sys->pairs_capacity * sizeof(NeighborPair));
                }
                sys->pairs[sys->n_pairs].i = i;
                sys->pairs[sys->n_pairs].j = j;
                sys->n_pairs++;
            }
        }
    }
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].last_pos = sys->particles[i].pos;
    }
}

void check_neighbor_rebuild(LJSystem *sys) {
    double max_dr2 = 0.0;
    for (int i = 0; i < sys->n_particles; i++) {
        Vector3 dr = {
            sys->particles[i].pos.x - sys->particles[i].last_pos.x,
            sys->particles[i].pos.y - sys->particles[i].last_pos.y,
            sys->particles[i].pos.z - sys->particles[i].last_pos.z
        };
        dr = min_image(dr, sys->box_len);
        double dr2 = dr.x*dr.x + dr.y*dr.y + dr.z*dr.z;
        if (dr2 > max_dr2) max_dr2 = dr2;
    }
    if (2.0 * sqrt(max_dr2) > RSKIN) {
        rebuild_neighbor_list(sys);
    }
}

double compute_forces(LJSystem *sys) {
    double pe = 0.0;
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].force.x = 0.0;
        sys->particles[i].force.y = 0.0;
        sys->particles[i].force.z = 0.0;
    }

    for (int idx = 0; idx < sys->n_pairs; idx++) {
        int i = sys->pairs[idx].i;
        int j = sys->pairs[idx].j;
        Vector3 dr = {
            sys->particles[i].pos.x - sys->particles[j].pos.x,
            sys->particles[i].pos.y - sys->particles[j].pos.y,
            sys->particles[i].pos.z - sys->particles[j].pos.z
        };
        dr = min_image(dr, sys->box_len);
        double r2 = dr.x*dr.x + dr.y*dr.y + dr.z*dr.z;
        if (r2 < RCUT2) {
            double inv_r2 = 1.0 / r2;
            double inv_r6 = inv_r2 * inv_r2 * inv_r2;
            double f_scalar = 48.0 * inv_r6 * (inv_r6 - 0.5) * inv_r2;

            sys->particles[i].force.x += f_scalar * dr.x;
            sys->particles[i].force.y += f_scalar * dr.y;
            sys->particles[i].force.z += f_scalar * dr.z;

            sys->particles[j].force.x -= f_scalar * dr.x;
            sys->particles[j].force.y -= f_scalar * dr.y;
            sys->particles[j].force.z -= f_scalar * dr.z;

            pe += 4.0 * inv_r6 * (inv_r6 - 1.0);
        }
    }
    return pe;
}

void apply_berendsen_thermostat(LJSystem *sys, double dt, double inst_temp) {
    if (inst_temp <= 1e-10) return;
    double lam = sqrt(1.0 + (dt / TAU_TEMP) * (sys->target_temp / inst_temp - 1.0));
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].vel.x *= lam;
        sys->particles[i].vel.y *= lam;
        sys->particles[i].vel.z *= lam;
    }
}

void init_fcc(LJSystem *sys) {
    int n_side = (int)ceil(cbrt(sys->n_particles / 4.0));
    double a = sys->box_len / n_side;
    int idx = 0;
    for (int ix = 0; ix < n_side && idx < sys->n_particles; ix++) {
        for (int iy = 0; iy < n_side && idx < sys->n_particles; iy++) {
            for (int iz = 0; iz < n_side && idx < sys->n_particles; iz++) {
                double bx = ix * a, by = iy * a, bz = iz * a;
                Vector3 basis[4] = {
                    {bx, by, bz},
                    {bx + 0.5*a, by + 0.5*a, bz},
                    {bx + 0.5*a, by, bz + 0.5*a},
                    {bx, by + 0.5*a, bz + 0.5*a}
                };
                for (int b = 0; b < 4 && idx < sys->n_particles; b++) {
                    sys->particles[idx].pos = basis[b];
                    idx++;
                }
            }
        }
    }
}

void init_velocities(LJSystem *sys) {
    double sum_vx = 0, sum_vy = 0, sum_vz = 0;
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].vel.x = ((double)rand() / RAND_MAX - 0.5);
        sys->particles[i].vel.y = ((double)rand() / RAND_MAX - 0.5);
        sys->particles[i].vel.z = ((double)rand() / RAND_MAX - 0.5);
        sum_vx += sys->particles[i].vel.x;
        sum_vy += sys->particles[i].vel.y;
        sum_vz += sys->particles[i].vel.z;
    }
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].vel.x -= sum_vx / sys->n_particles;
        sys->particles[i].vel.y -= sum_vy / sys->n_particles;
        sys->particles[i].vel.z -= sum_vz / sys->n_particles;
    }
    double v2_sum = 0;
    for (int i = 0; i < sys->n_particles; i++) {
        v2_sum += sys->particles[i].vel.x*sys->particles[i].vel.x +
                  sys->particles[i].vel.y*sys->particles[i].vel.y +
                  sys->particles[i].vel.z*sys->particles[i].vel.z;
    }
    double current_temp = v2_sum / (3.0 * sys->n_particles);
    double scale = sqrt(sys->target_temp / current_temp);
    for (int i = 0; i < sys->n_particles; i++) {
        sys->particles[i].vel.x *= scale;
        sys->particles[i].vel.y *= scale;
        sys->particles[i].vel.z *= scale;
    }
}

int main(void) {
    double density = 0.8442;
    LJSystem sys;
    sys.n_particles = N_PARTICLES;
    sys.target_temp = 0.728;
    sys.box_len = cbrt(N_PARTICLES / density);
    sys.particles = (Particle*)malloc(N_PARTICLES * sizeof(Particle));
    sys.pairs_capacity = N_PARTICLES * 32;
    sys.pairs = (NeighborPair*)malloc(sys.pairs_capacity * sizeof(NeighborPair));

    init_fcc(&sys);
    init_velocities(&sys);
    rebuild_neighbor_list(&sys);

    double pe = compute_forces(&sys);
    printf("Step\tKinetic_E\tPotential_E\tTotal_E\t\tTemp*\n");

    for (int step = 0; step <= N_STEPS; step++) {
        for (int i = 0; i < N_PARTICLES; i++) {
            sys.particles[i].pos.x += sys.particles[i].vel.x * DT + 0.5 * sys.particles[i].force.x * DT * DT;
            sys.particles[i].pos.y += sys.particles[i].vel.y * DT + 0.5 * sys.particles[i].force.y * DT * DT;
            sys.particles[i].pos.z += sys.particles[i].vel.z * DT + 0.5 * sys.particles[i].force.z * DT * DT;

            sys.particles[i].pos.x -= sys.box_len * floor(sys.particles[i].pos.x / sys.box_len);
            sys.particles[i].pos.y -= sys.box_len * floor(sys.particles[i].pos.y / sys.box_len);
            sys.particles[i].pos.z -= sys.box_len * floor(sys.particles[i].pos.z / sys.box_len);

            sys.particles[i].vel.x += 0.5 * sys.particles[i].force.x * DT;
            sys.particles[i].vel.y += 0.5 * sys.particles[i].force.y * DT;
            sys.particles[i].vel.z += 0.5 * sys.particles[i].force.z * DT;
        }

        check_neighbor_rebuild(&sys);
        pe = compute_forces(&sys);

        double ke = 0.0;
        for (int i = 0; i < N_PARTICLES; i++) {
            sys.particles[i].vel.x += 0.5 * sys.particles[i].force.x * DT;
            sys.particles[i].vel.y += 0.5 * sys.particles[i].force.y * DT;
            sys.particles[i].vel.z += 0.5 * sys.particles[i].force.z * DT;

            ke += 0.5 * (sys.particles[i].vel.x*sys.particles[i].vel.x +
                        sys.particles[i].vel.y*sys.particles[i].vel.y +
                        sys.particles[i].vel.z*sys.particles[i].vel.z);
        }

        double inst_temp = (2.0 * ke) / (3.0 * N_PARTICLES);
        if (step < 500) {
            apply_berendsen_thermostat(&sys, DT, inst_temp);
        }

        if (step % 100 == 0) {
            printf("%d\t%.4f\t\t%.4f\t\t%.4f\t\t%.4f\n",
                   step, ke / N_PARTICLES, pe / N_PARTICLES, (ke + pe) / N_PARTICLES, inst_temp);
        }
    }

    free(sys.pairs);
    free(sys.particles);
    return 0;
}
