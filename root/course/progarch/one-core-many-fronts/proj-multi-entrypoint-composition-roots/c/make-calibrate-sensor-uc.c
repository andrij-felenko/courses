#include <stdbool.h>

/* Outbound port: структура з покажчиком на операцію сховища */
typedef struct {
    bool (*save_calibration)(void *ctx, const char *sensor_id, double offset);
    void *ctx;
} sensor_repo_t;

/* Inbound port: сценарій використання */
typedef struct {
    sensor_repo_t repo;
} calibrate_sensor_uc_t;

static inline calibrate_sensor_uc_t make_calibrate_sensor_uc(sensor_repo_t repo) {
    return (calibrate_sensor_uc_t){ .repo = repo };
}

static inline bool calibrate_sensor_execute(const calibrate_sensor_uc_t *uc, const char *id, double offset) {
    if (offset < -10.0 || offset > 10.0) return false;
    return uc->repo.save_calibration(uc->repo.ctx, id, offset);
}
