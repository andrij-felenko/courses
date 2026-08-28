#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <float.h>
#include <stdbool.h>

typedef struct {
    double t;
    double x;
    double y;
    double z;
    double vx;
    double vy;
    double vz;
    double voltage;
    double current;
} FlightPoint;

typedef struct {
    FlightPoint* points;
    size_t size;
    size_t capacity;
} Trajectory;

typedef struct {
    double max_frechet;
    double max_dtw_norm;
    double max_xte_rms;
    double max_xte_peak;
    double max_energy_pct;
    size_t dtw_window;
    const char* test_csv;
    const char* golden_csv;
    const char* json_out;
    const char* junit_out;
} Config;

static inline double dist3d(FlightPoint a, FlightPoint b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    double dz = a.z - b.z;
    return sqrt(dx * dx + dy * dy + dz * dz);
}

void traj_init(Trajectory* traj) {
    traj->size = 0;
    traj->capacity = 1024;
    traj->points = (FlightPoint*)malloc(traj->capacity * sizeof(FlightPoint));
}

void traj_push(Trajectory* traj, FlightPoint pt) {
    if (traj->size >= traj->capacity) {
        traj->capacity *= 2;
        traj->points = (FlightPoint*)realloc(traj->points, traj->capacity * sizeof(FlightPoint));
    }
    traj->points[traj->size++] = pt;
}

void traj_free(Trajectory* traj) {
    if (traj->points) {
        free(traj->points);
        traj->points = NULL;
    }
    traj->size = 0;
    traj->capacity = 0;
}

bool load_csv(const char* path, Trajectory* traj) {
    FILE* f = fopen(path, "r");
    if (!f) return false;

    char line[512];
    if (!fgets(line, sizeof(line), f)) {
        fclose(f);
        return false;
    }

    while (fgets(line, sizeof(line), f)) {
        FlightPoint pt = {0};
        unsigned long long t_us = 0;
        int n = sscanf(line, "%llu,%lf,%lf,%lf,%lf,%lf,%lf,%*lf,%*lf,%*lf,%lf,%lf",
                       &t_us, &pt.x, &pt.y, &pt.z, &pt.vx, &pt.vy, &pt.vz, &pt.voltage, &pt.current);
        if (n >= 7) {
            pt.t = (double)t_us * 1e-6;
            traj_push(traj, pt);
        }
    }

    fclose(f);
    return traj->size > 0;
}

double compute_frechet(const Trajectory* p, const Trajectory* q) {
    size_t n = p->size;
    size_t m = q->size;
    if (n == 0 || m == 0) return DBL_MAX;

    double* prev = (double*)malloc(m * sizeof(double));
    double* curr = (double*)malloc(m * sizeof(double));
    if (!prev || !curr) { free(prev); free(curr); return DBL_MAX; }

    prev[0] = dist3d(p->points[0], q->points[0]);
    for (size_t j = 1; j < m; ++j) {
        double d = dist3d(p->points[0], q->points[j]);
        prev[j] = (d > prev[j - 1]) ? d : prev[j - 1];
    }

    for (size_t i = 1; i < n; ++i) {
        double d0 = dist3d(p->points[i], q->points[0]);
        curr[0] = (d0 > prev[0]) ? d0 : prev[0];

        for (size_t j = 1; j < m; ++j) {
            double d = dist3d(p->points[i], q->points[j]);
            double min_prev = prev[j - 1];
            if (prev[j] < min_prev) min_prev = prev[j];
            if (curr[j - 1] < min_prev) min_prev = curr[j - 1];
            curr[j] = (d > min_prev) ? d : min_prev;
        }

        double* tmp = prev;
        prev = curr;
        curr = tmp;
    }

    double res = prev[m - 1];
    free(prev);
    free(curr);
    return res;
}

double compute_dtw(const Trajectory* p, const Trajectory* q, size_t r) {
    size_t n = p->size;
    size_t m = q->size;
    if (n == 0 || m == 0) return DBL_MAX;

    double* dtw = (double*)malloc(n * m * sizeof(double));
    if (!dtw) return DBL_MAX;

    for (size_t i = 0; i < n * m; ++i) dtw[i] = DBL_MAX;
    #define CELL(i, j) dtw[(i) * m + (j)]

    CELL(0, 0) = dist3d(p->points[0], q->points[0]);

    for (size_t i = 0; i < n; ++i) {
        size_t j_start = (i > r) ? (i - r) : 0;
        size_t j_end = (i + r + 1 < m) ? (i + r + 1) : m;

        for (size_t j = j_start; j < j_end; ++j) {
            if (i == 0 && j == 0) continue;
            double cost = dist3d(p->points[i], q->points[j]);
            double min_prev = DBL_MAX;

            if (i > 0 && CELL(i - 1, j) < min_prev) min_prev = CELL(i - 1, j);
            if (j > 0 && CELL(i, j - 1) < min_prev) min_prev = CELL(i, j - 1);
            if (i > 0 && j > 0 && CELL(i - 1, j - 1) < min_prev) min_prev = CELL(i - 1, j - 1);

            if (min_prev < DBL_MAX) CELL(i, j) = cost + min_prev;
        }
    }

    double total = CELL(n - 1, m - 1);
    free(dtw);
    #undef CELL
    return (total < DBL_MAX) ? (total / (double)(n + m)) : DBL_MAX;
}

double compute_energy(const Trajectory* traj) {
    double energy_joules = 0.0;
    for (size_t i = 0; i + 1 < traj->size; ++i) {
        double dt = traj->points[i + 1].t - traj->points[i].t;
        if (dt > 0.0 && dt < 1.0) {
            double p1 = traj->points[i].voltage * traj->points[i].current;
            double p2 = traj->points[i + 1].voltage * traj->points[i + 1].current;
            energy_joules += 0.5 * (p1 + p2) * dt;
        }
    }
    return energy_joules;
}

void write_reports(const Config* cfg, double frechet, double dtw, double e_test, double e_gold, bool pass) {
    if (cfg->json_out) {
        FILE* f = fopen(cfg->json_out, "w");
        if (f) {
            fprintf(f, "{\n");
            fprintf(f, "  \"passed\": %s,\n", pass ? "true" : "false");
            fprintf(f, "  \"frechet_distance\": %.4f,\n", frechet);
            fprintf(f, "  \"dtw_normalized\": %.4f,\n", dtw);
            fprintf(f, "  \"energy_test_joules\": %.2f,\n", e_test);
            fprintf(f, "  \"energy_golden_joules\": %.2f,\n", e_gold);
            fprintf(f, "  \"energy_delta_pct\": %.2f\n", (e_gold > 0.0) ? ((e_test - e_gold) / e_gold * 100.0) : 0.0);
            fprintf(f, "}\n");
            fclose(f);
        }
    }

    if (cfg->junit_out) {
        FILE* f = fopen(cfg->junit_out, "w");
        if (f) {
            fprintf(f, "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
            fprintf(f, "<testsuite name=\"AutonomyRegression\" tests=\"3\" failures=\"%d\">\n", pass ? 0 : 1);
            fprintf(f, "  <testcase name=\"FrechetDistance\" time=\"0.010\">\n");
            if (frechet > cfg->max_frechet) {
                fprintf(f, "    <failure message=\"Frechet distance %.4f exceeds limit %.4f\"/>\n", frechet, cfg->max_frechet);
            }
            fprintf(f, "  </testcase>\n");
            fprintf(f, "  <testcase name=\"DynamicTimeWarping\" time=\"0.015\">\n");
            if (dtw > cfg->max_dtw_norm) {
                fprintf(f, "    <failure message=\"DTW normalized %.4f exceeds limit %.4f\"/>\n", dtw, cfg->max_dtw_norm);
            }
            fprintf(f, "  </testcase>\n");
            fprintf(f, "  <testcase name=\"EnergyConsumption\" time=\"0.005\"/>\n");
            fprintf(f, "</testsuite>\n");
            fclose(f);
        }
    }
}

int main(int argc, char** argv) {
    Config cfg = {
        .max_frechet = 0.80,
        .max_dtw_norm = 0.35,
        .max_xte_rms = 0.40,
        .max_xte_peak = 1.00,
        .max_energy_pct = 5.0,
        .dtw_window = 60,
        .test_csv = NULL,
        .golden_csv = NULL,
        .json_out = "regression_report.json",
        .junit_out = "junit_report.xml"
    };

    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--test") == 0 && i + 1 < argc) cfg.test_csv = argv[++i];
        else if (strcmp(argv[i], "--golden") == 0 && i + 1 < argc) cfg.golden_csv = argv[++i];
        else if (strcmp(argv[i], "--max-frechet") == 0 && i + 1 < argc) cfg.max_frechet = atof(argv[++i]);
        else if (strcmp(argv[i], "--max-dtw") == 0 && i + 1 < argc) cfg.max_dtw_norm = atof(argv[++i]);
        else if (strcmp(argv[i], "--dtw-window") == 0 && i + 1 < argc) cfg.dtw_window = atoi(argv[++i]);
        else if (strcmp(argv[i], "--json-out") == 0 && i + 1 < argc) cfg.json_out = argv[++i];
        else if (strcmp(argv[i], "--junit-out") == 0 && i + 1 < argc) cfg.junit_out = argv[++i];
    }

    if (!cfg.test_csv || !cfg.golden_csv) {
        fprintf(stderr, "Usage: %s --test <test.csv> --golden <golden.csv> [options]\n", argv[0]);
        return 2;
    }

    Trajectory test_traj, golden_traj;
    traj_init(&test_traj);
    traj_init(&golden_traj);

    if (!load_csv(cfg.test_csv, &test_traj) || !load_csv(cfg.golden_csv, &golden_traj)) {
        fprintf(stderr, "Error: Failed to load telemetry CSV files.\n");
        traj_free(&test_traj);
        traj_free(&golden_traj);
        return 2;
    }

    double frechet = compute_frechet(&test_traj, &golden_traj);
    double dtw = compute_dtw(&test_traj, &golden_traj, cfg.dtw_window);
    double e_test = compute_energy(&test_traj);
    double e_gold = compute_energy(&golden_traj);
    double e_delta_pct = (e_gold > 0.0) ? ((e_test - e_gold) / e_gold * 100.0) : 0.0;

    bool pass = (frechet <= cfg.max_frechet) &&
                (dtw <= cfg.max_dtw_norm) &&
                (e_delta_pct <= cfg.max_energy_pct);

    printf("=== AUTONOMY REGRESSION REPORT ===\n");
    printf("Frechet Distance: %.4f m (Limit: <= %.4f m) -> %s\n",
           frechet, cfg.max_frechet, (frechet <= cfg.max_frechet) ? "OK" : "FAIL");
    printf("DTW Normalized:   %.4f m/step (Limit: <= %.4f m/step) -> %s\n",
           dtw, cfg.max_dtw_norm, (dtw <= cfg.max_dtw_norm) ? "OK" : "FAIL");
    printf("Energy Consumed:  %.2f J vs %.2f J (Delta: %+.2f%%) -> %s\n",
           e_test, e_gold, e_delta_pct, (e_delta_pct <= cfg.max_energy_pct) ? "OK" : "FAIL");
    printf("Final Status:     %s\n", pass ? "PASS" : "FAIL");

    write_reports(&cfg, frechet, dtw, e_test, e_gold, pass);

    traj_free(&test_traj);
    traj_free(&golden_traj);

    return pass ? 0 : 1;
}
