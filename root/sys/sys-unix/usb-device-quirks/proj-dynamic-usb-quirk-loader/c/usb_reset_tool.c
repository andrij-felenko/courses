// usb_reset_tool.c — Скидання USB-пристрою через USBDEVFS_RESET (чистий C)
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/ioctl.h>
#include <linux/usbdevice_fs.h>
#include <errno.h>

static int find_and_reset_usb(int target_vid, int target_pid) {
    const char *usb_base = "/dev/bus/usb";
    DIR *bus_dir = opendir(usb_base);
    if (!bus_dir) {
        perror("Помилка відкриття /dev/bus/usb");
        return -1;
    }

    struct dirent *bus_entry;
    int found = 0;

    while ((bus_entry = readdir(bus_dir)) != NULL) {
        if (bus_entry->d_name[0] == '.') continue;

        char bus_path[256];
        snprintf(bus_path, sizeof(bus_path), "%s/%s", usb_base, bus_entry->d_name);

        DIR *dev_dir = opendir(bus_path);
        if (!dev_dir) continue;

        struct dirent *dev_entry;
        while ((dev_entry = readdir(dev_dir)) != NULL) {
            if (dev_entry->d_name[0] == '.') continue;

            char dev_path[512];
            snprintf(dev_path, sizeof(dev_path), "%s/%s", bus_path, dev_entry->d_name);

            int fd = open(dev_path, O_RDWR);
            if (fd < 0) continue;

            // Зчитування стандартного 18-байтового дескриптора пристрою
            unsigned char desc[18];
            if (read(fd, desc, sizeof(desc)) == sizeof(desc)) {
                int vid = desc[8] | (desc[9] << 8);
                int pid = desc[10] | (desc[11] << 8);

                if (vid == target_vid && pid == target_pid) {
                    printf("Знайдено пристрій %04x:%04x на %s\n", vid, pid, dev_path);
                    printf("Виконання USBDEVFS_RESET ioctl...\n");

                    if (ioctl(fd, USBDEVFS_RESET, 0) < 0) {
                        fprintf(stderr, "Помилка ioctl USBDEVFS_RESET: %s\n", strerror(errno));
                        close(fd);
                        closedir(dev_dir);
                        closedir(bus_dir);
                        return -1;
                    }

                    printf("Скидання USB-пристрою успішно завершено.\n");
                    found = 1;
                    close(fd);
                    break;
                }
            }
            close(fd);
        }
        closedir(dev_dir);
        if (found) break;
    }

    closedir(bus_dir);
    if (!found) {
        fprintf(stderr, "Пристрій %04x:%04x не знайдено на шині USB.\n", target_vid, target_pid);
        return -1;
    }
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <VID_hex> <PID_hex>\n", argv[0]);
        fprintf(stderr, "Приклад: %s 04b4 8613\n", argv[0]);
        return 1;
    }

    int vid = (int)strtol(argv[1], NULL, 16);
    int pid = (int)strtol(argv[2], NULL, 16);

    return find_and_reset_usb(vid, pid) == 0 ? 0 : 1;
}
