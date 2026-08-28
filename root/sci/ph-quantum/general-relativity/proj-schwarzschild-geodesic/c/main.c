#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double phi;
    double r;
    double u;
    double w;
} GeodesicPoint;

typedef struct {
    GeodesicPoint* data;
    size_t size;
    size_t capacity;
} GeodesicBuffer;

static void rhs_c(double u, double w, double r_s, double* du, double* dw) {
    *du = w;
    *dw = 1.5 * r_s * u * u - u;
}

GeodesicBuffer* create_geodesic_buffer(size_t initial_capacity) {
    GeodesicBuffer* buf = (GeodesicBuffer*)malloc(sizeof(GeodesicBuffer));
    if (!buf) return NULL;
    buf->size = 0;
    buf->capacity = initial_capacity > 0 ? initial_capacity : 1024;
    buf->data = (GeodesicPoint*)malloc(buf->capacity * sizeof(GeodesicPoint));
    if (!buf->data) {
        free(buf);
        return NULL;
    }
    return buf;
}

void free_geodesic_buffer(GeodesicBuffer* buf) {
    if (buf) {
        free(buf->data);
        free(buf);
    }
}

int append_geodesic_point(GeodesicBuffer* buf, GeodesicPoint pt) {
    if (buf->size >= buf->capacity) {
        size_t new_cap = buf->capacity * 2;
        GeodesicPoint* new_data = (GeodesicPoint*)realloc(buf->data, new_cap * sizeof(GeodesicPoint));
        if (!new_data) return 0;
        buf->data = new_data;
        buf->capacity = new_cap;
    }
    buf->data[buf->size++] = pt;
    return 1;
}

GeodesicBuffer* simulate_schwarzschild_c(double r_init, double b, double r_s, double dphi, size_t max_steps) {
    GeodesicBuffer* buf = create_geodesic_buffer(2048);
    if (!buf) return NULL;

    double u = 1.0 / r_init;
    double w_sq = 1.0 / (b * b) - u * u * (1.0 - r_s * u);
    double w = sqrt(fmax(0.0, w_sq));
    double phi = 0.0;

    for (size_t step = 0; step < max_steps; ++step) {
        double r_curr = (u > 1e-15) ? (1.0 / u) : 1e15;
        GeodesicPoint pt = { phi, r_curr, u, w };
        if (!append_geodesic_point(buf, pt)) break;

        if (u >= 1.0 / r_s) {
            // Захоплення горизонтом подій
            break;
        }

        if (u <= 0.0 && phi > 1.57079632679) {
            // Виліт у безкінечність
            break;
        }

        double k1_u, k1_w, k2_u, k2_w, k3_u, k3_w, k4_u, k4_w;
        rhs_c(u, w, r_s, &k1_u, &k1_w);
        rhs_c(u + 0.5 * dphi * k1_u, w + 0.5 * dphi * k1_w, r_s, &k2_u, &k2_w);
        rhs_c(u + 0.5 * dphi * k2_u, w + 0.5 * dphi * k2_w, r_s, &k3_u, &k3_w);
        rhs_c(u + dphi * k3_u, w + dphi * k3_w, r_s, &k4_u, &k4_w);

        u += (dphi / 6.0) * (k1_u + 2.0 * k2_u + 2.0 * k3_u + k4_u);
        w += (dphi / 6.0) * (k1_w + 2.0 * k2_w + 2.0 * k3_w + k4_w);
        phi += dphi;
    }

    return buf;
}

int main(void) {
    double r_s = 2950.0;
    double b = 6.96e8;
    GeodesicBuffer* traj = simulate_schwarzschild_c(1.0e11, b, r_s, 0.0005, 50000);

    if (traj) {
        printf("C-симуляція: обчислено %zu точок геодезичної лінії.\n", traj->size);
        if (traj->size > 0) {
            double final_phi = traj->data[traj->size - 1].phi;
            double defl = fabs(final_phi - 3.141592653589793) * (180.0 / 3.141592653589793) * 3600.0;
            printf("Кут відхилення світла Сонцем: %.3f кутових секунд.\n", defl);
        }
        free_geodesic_buffer(traj);
    }
    return 0;
}
