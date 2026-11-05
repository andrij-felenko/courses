#include "compensation_table.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>

#define INITIAL_CAPACITY 32
#define MAX_LINE_LENGTH  512

bool comp_table_init(compensation_table_t *table, const abbe_arm_t *arm, angle_unit_t unit) {
    if (!table || !arm) {
        return false;
    }

    table->samples = (angle_sample_t *)malloc(INITIAL_CAPACITY * sizeof(angle_sample_t));
    if (!table->samples) {
        return false;
    }

    table->entries       = NULL;
    table->count         = 0;
    table->capacity      = INITIAL_CAPACITY;
    table->arm           = *arm;
    table->unit          = unit;
    table->step_mm       = 0.0;
    table->is_calculated = false;

    return true;
}

void comp_table_free(compensation_table_t *table) {
    if (!table) {
        return;
    }

    free(table->samples);
    free(table->entries);
    table->samples       = NULL;
    table->entries       = NULL;
    table->count         = 0;
    table->capacity      = 0;
    table->is_calculated = false;
}

static bool comp_table_append(compensation_table_t *table, const angle_sample_t *sample) {
    if (table->count >= table->capacity) {
        size_t new_cap = table->capacity * 2;
        angle_sample_t *new_buf = (angle_sample_t *)realloc(table->samples, new_cap * sizeof(angle_sample_t));
        if (!new_buf) {
            return false;
        }
        table->samples  = new_buf;
        table->capacity = new_cap;
    }

    table->samples[table->count] = *sample;
    table->count++;
    return true;
}

bool comp_table_load_stream(compensation_table_t *table, FILE *stream) {
    if (!table || !stream) {
        return false;
    }

    char line[MAX_LINE_LENGTH];

    while (fgets(line, sizeof(line), stream)) {
        char *ptr = line;

        /* Пропуск початкових пробільних символів */
        while (*ptr && isspace((unsigned char)*ptr)) {
            ptr++;
        }

        /* Пропуск порожніх рядків та рядків-коментарів (#, ;, //, %) */
        if (*ptr == '\0' || *ptr == '#' || *ptr == ';' || *ptr == '%' ||
            (ptr[0] == '/' && ptr[1] == '/')) {
            continue;
        }

        /* Пропуск заголовка таблиці, якщо він містить літерні позначення стовпців */
        if (isalpha((unsigned char)*ptr)) {
            continue;
        }

        /*
         * Розбір трьох числових значень: координата X, кут тангажу (pitch), кут рискання (yaw).
         * Роздільниками можуть бути пробіли, табуляції або коми.
         */
        char *endptr = NULL;
        double pos_x = strtod(ptr, &endptr);
        if (endptr == ptr) {
            continue;
        }
        ptr = endptr;

        while (*ptr && (*ptr == ',' || isspace((unsigned char)*ptr))) {
            ptr++;
        }

        double pitch = strtod(ptr, &endptr);
        if (endptr == ptr) {
            continue;
        }
        ptr = endptr;

        while (*ptr && (*ptr == ',' || isspace((unsigned char)*ptr))) {
            ptr++;
        }

        double yaw = strtod(ptr, &endptr);
        if (endptr == ptr) {
            continue;
        }

        angle_sample_t sample;
        sample.position_x = pos_x;
        sample.pitch      = pitch;
        sample.yaw        = yaw;

        if (!comp_table_append(table, &sample)) {
            return false;
        }
    }

    return (table->count >= 2);
}

bool comp_table_load_file(compensation_table_t *table, const char *filepath) {
    if (!table || !filepath) {
        return false;
    }

    FILE *f = fopen(filepath, "r");
    if (!f) {
        return false;
    }

    bool res = comp_table_load_stream(table, f);
    fclose(f);
    return res;
}

bool comp_table_validate(compensation_table_t *table) {
    if (!table || table->count < 2) {
        return false;
    }

    /* Перевірка суворо монотонного зростання координат позиціонування */
    for (size_t i = 1; i < table->count; i++) {
        if (table->samples[i].position_x <= table->samples[i - 1].position_x) {
            return false;
        }
    }

    /* Визначення номінального кроку дискретизації */
    double total_span = table->samples[table->count - 1].position_x - table->samples[0].position_x;
    double nom_step   = total_span / (double)(table->count - 1);
    table->step_mm    = nom_step;

    return true;
}

bool comp_table_compute(compensation_table_t *table) {
    if (!table || table->count == 0) {
        return false;
    }

    /* Виділення пам'яті під результуючий масив поправок */
    free(table->entries);
    table->entries = (compensation_entry_t *)malloc(table->count * sizeof(compensation_entry_t));
    if (!table->entries) {
        return false;
    }

    if (!abbe_calculate_batch(&table->arm, table->samples, table->count, table->unit, table->entries)) {
        free(table->entries);
        table->entries = NULL;
        return false;
    }

    table->is_calculated = true;
    return true;
}

bool comp_table_export_csv(const compensation_table_t *table, const char *filepath) {
    if (!table || !filepath || !table->is_calculated || !table->entries) {
        return false;
    }

    FILE *f = fopen(filepath, "w");
    if (!f) {
        return false;
    }

    /* Метадані та інформаційний заголовок */
    fprintf(f, "# Abbe Error Compensation Table\n");
    fprintf(f, "# Abbe Arm: dy=%.3f mm, dz=%.3f mm\n", table->arm.dy, table->arm.dz);
    fprintf(f, "# Angular Units: %s\n", abbe_unit_to_string(table->unit));
    fprintf(f, "Index,Position_X_mm,Pitch_rad,Yaw_rad,Error_Pitch_um,Error_Yaw_um,Total_Error_um,Correction_um,Corrected_X_mm\n");

    for (size_t i = 0; i < table->count; i++) {
        const compensation_entry_t *e = &table->entries[i];
        double err_pitch_um = e->error_pitch_mm * 1000.0;
        double err_yaw_um   = e->error_yaw_mm * 1000.0;
        double total_err_um = e->total_error_mm * 1000.0;
        double corr_um      = e->correction_mm * 1000.0;
        double corrected_x  = e->position_x + e->correction_mm;

        fprintf(f, "%zu,%.4f,%.8e,%.8e,%.4f,%.4f,%.4f,%.4f,%.6f\n",
                i,
                e->position_x,
                e->pitch_rad,
                e->yaw_rad,
                err_pitch_um,
                err_yaw_um,
                total_err_um,
                corr_um,
                corrected_x);
    }

    fclose(f);
    return true;
}

bool comp_table_export_cnc(const compensation_table_t *table, const char *filepath, const char *axis_name) {
    if (!table || !filepath || !table->is_calculated || !table->entries) {
        return false;
    }

    const char *axis = (axis_name && axis_name[0] != '\0') ? axis_name : "X";
    FILE *f = fopen(filepath, "w");
    if (!f) {
        return false;
    }

    double start_pos = table->entries[0].position_x;
    double end_pos   = table->entries[table->count - 1].position_x;

    /* Стандартизований заголовок файлу компенсації кроку для систем ЧПУ (Fanuc, LinuxCNC) */
    fprintf(f, "; ================================================================\n");
    fprintf(f, "; CNC Pitch Error Compensation Table (Abbe Error Compensation)\n");
    fprintf(f, "; Target Axis: %s\n", axis);
    fprintf(f, "; Abbe Arm: dy = %.3f mm, dz = %.3f mm\n", table->arm.dy, table->arm.dz);
    fprintf(f, "; Total Calibration Points: %zu\n", table->count);
    fprintf(f, "; Position Range: Start = %.4f mm, Step = %.4f mm, End = %.4f mm\n",
            start_pos, table->step_mm, end_pos);
    fprintf(f, "; Units: Position in mm, Linear Compensation in mm\n");
    fprintf(f, "; Format: <Point_Index>  <Target_Position_mm>  <Compensation_mm>\n");
    fprintf(f, "; ================================================================\n");

    for (size_t i = 0; i < table->count; i++) {
        fprintf(f, "%-8zu %-18.4f %-18.6f\n",
                i,
                table->entries[i].position_x,
                table->entries[i].correction_mm);
    }

    fclose(f);
    return true;
}

bool comp_table_get_stats(const compensation_table_t *table, compensation_stats_t *stats) {
    if (!table || !stats || !table->is_calculated || table->count == 0) {
        return false;
    }

    stats->count        = table->count;
    stats->start_pos_mm = table->entries[0].position_x;
    stats->end_pos_mm   = table->entries[table->count - 1].position_x;
    stats->step_mm      = table->step_mm;

    double min_err_um = table->entries[0].total_error_mm * 1000.0;
    double max_err_um = min_err_um;
    double max_abs_corr_um = fabs(table->entries[0].correction_mm * 1000.0);

    for (size_t i = 1; i < table->count; i++) {
        double err_um  = table->entries[i].total_error_mm * 1000.0;
        double corr_um = fabs(table->entries[i].correction_mm * 1000.0);

        if (err_um < min_err_um) {
            min_err_um = err_um;
        }
        if (err_um > max_err_um) {
            max_err_um = err_um;
        }
        if (corr_um > max_abs_corr_um) {
            max_abs_corr_um = corr_um;
        }
    }

    stats->min_error_um      = min_err_um;
    stats->max_error_um      = max_err_um;
    stats->peak_to_peak_um   = max_err_um - min_err_um;
    stats->max_correction_um = max_abs_corr_um;

    return true;
}
