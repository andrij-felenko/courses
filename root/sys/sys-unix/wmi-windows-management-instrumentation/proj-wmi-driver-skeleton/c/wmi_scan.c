// wmi_scan.c — Процедурна версія мовою C (POSIX API)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>

#define SYSFS_WMI_PATH "/sys/bus/wmi/devices"

void inspect_wmi_device(const char *dev_name) {
    char path[512];
    FILE *fp;
    char buffer[128];

    snprintf(path, sizeof(path), "%s/%s/object_id", SYSFS_WMI_PATH, dev_name);
    fp = fopen(path, "r");
    if (!fp) return;

    if (fgets(buffer, sizeof(buffer), fp)) {
        buffer[strcspn(buffer, "\r\n")] = 0;
        printf("WMI Device: %-36s | Object ID: %s\n", dev_name, buffer);
    }
    fclose(fp);
}

int main(void) {
    DIR *dir = opendir(SYSFS_WMI_PATH);
    if (!dir) {
        perror("Не вдалося відкрити " SYSFS_WMI_PATH);
        return EXIT_FAILURE;
    }

    struct dirent *entry;
    printf("=== Сканування WMI пристроїв Linux (C) ===\n");
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;
        inspect_wmi_device(entry->d_name);
    }

    closedir(dir);
    return EXIT_SUCCESS;
}
