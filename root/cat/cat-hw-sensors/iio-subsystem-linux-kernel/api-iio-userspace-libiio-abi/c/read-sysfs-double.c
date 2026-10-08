#include <stdio.h>
#include <stdlib.h>

static int read_sysfs_double(const char *path, double *val) {
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;
    if (fscanf(fp, "%lf", val) != 1) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    return 0;
}

static int read_sysfs_int(const char *path, long *val) {
    FILE *fp = fopen(path, "r");
    if (!fp) return -1;
    if (fscanf(fp, "%ld", val) != 1) {
        fclose(fp);
        return -1;
    }
    fclose(fp);
    return 0;
}

int main(void) {
    long raw = 0;
    double scale = 1.0, offset = 0.0;
    
    const char *base = "/sys/bus/iio/devices/iio:device0/";
    char path_raw[256], path_scale[256], path_offset[256];
    
    snprintf(path_raw, sizeof(path_raw), "%sin_accel_x_raw", base);
    snprintf(path_scale, sizeof(path_scale), "%sin_accel_x_scale", base);
    snprintf(path_offset, sizeof(path_offset), "%sin_accel_x_offset", base);

    if (read_sysfs_int(path_raw, &raw) < 0) {
        perror("Не вдалося прочитати raw");
        return EXIT_FAILURE;
    }
    read_sysfs_double(path_scale, &scale);
    read_sysfs_double(path_offset, &offset);

    double accel_x_m_s2 = (raw + offset) * scale;
    printf("Прискорення X: %.6f m/s^2 (raw=%ld, offset=%.2f, scale=%.8f)\n",
           accel_x_m_s2, raw, offset, scale);
    return EXIT_SUCCESS;
}
