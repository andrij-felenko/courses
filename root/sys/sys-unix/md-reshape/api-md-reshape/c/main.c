#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

static int read_sysfs_value(const char *path, char *out_buf, size_t max_size) {
    FILE *file_ptr = fopen(path, "r");
    if (!file_ptr) {
        return -1;
    }
    if (!fgets(out_buf, (int)max_size, file_ptr)) {
        fclose(file_ptr);
        return -1;
    }
    fclose(file_ptr);
    out_buf[strcspn(out_buf, "\r\n")] = '\0';
    return 0;
}

int main(int argc, char *argv[]) {
    const char *array_name = (argc > 1) ? argv[1] : "md0";
    char file_path[256];
    char action_str[64] = {0};
    char completed_str[128] = {0};
    char speed_str[64] = {0};
    char direction_str[64] = {0};

    snprintf(file_path, sizeof(file_path), "/sys/block/%s/md/sync_action", array_name);
    if (read_sysfs_value(file_path, action_str, sizeof(action_str)) < 0) {
        fprintf(stderr, "Помилка: не вдалося відкрити атрибути пристрою %s у sysfs\n", array_name);
        return 1;
    }

    if (strcmp(action_str, "reshape") != 0) {
        printf("Масив %s не перебудовується (поточний стан: %s)\n", array_name, action_str);
        return 0;
    }

    snprintf(file_path, sizeof(file_path), "/sys/block/%s/md/sync_completed", array_name);
    read_sysfs_value(file_path, completed_str, sizeof(completed_str));

    snprintf(file_path, sizeof(file_path), "/sys/block/%s/md/sync_speed", array_name);
    read_sysfs_value(file_path, speed_str, sizeof(speed_str));

    snprintf(file_path, sizeof(file_path), "/sys/block/%s/md/reshape_direction", array_name);
    read_sysfs_value(file_path, direction_str, sizeof(direction_str));

    printf("Стан масиву %s: активна перебудова (reshape)\n", array_name);
    printf("  Напрямок руху смуг  : %s\n", direction_str[0] ? direction_str : "невідомо");
    printf("  Прогрес у секторах  : %s\n", completed_str);
    printf("  Поточна швидкість   : %s КіБ/с\n", speed_str);

    return 0;
}
