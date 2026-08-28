#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int id;
    double scale;
} TransformConfig;

/* Захисне C-програмування: перевірка на null у кожній функції */
void apply_transform_c(const TransformConfig* cfg, double* value) {
    if (cfg == NULL || value == NULL) {
        return; /* Прихований збій або дублювання перевірок */
    }
    *value = (*value) * cfg->scale;
}
