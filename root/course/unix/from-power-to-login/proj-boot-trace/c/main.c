#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <time.h>

#define EFIVARS_PATH "/sys/firmware/efi/efivars"
#define CMDLINE_PATH "/proc/cmdline"
#define UPTIME_PATH  "/proc/uptime"

typedef struct {
    uint64_t firmware_usec;
    uint64_t loader_usec;
    uint64_t kernel_usec;
    uint64_t initrd_usec;
    uint64_t userspace_usec;
    uint64_t total_usec;
    int is_efi;
    char root_param[256];
    char init_param[256];
    char target_unit[256];
} BootTelemetry;

/* Зчитування 64-бітної змінної UEFI з віртуального каталогу efivars */
static int read_efivar_u64(const char *prefix, uint64_t *out_val) {
    DIR *dir = opendir(EFIVARS_PATH);
    if (!dir) {
        return -1;
    }

    struct dirent *entry;
    char target_file[512] = {0};
    size_t prefix_len = strlen(prefix);

    while ((entry = readdir(dir)) != NULL) {
        if (strncmp(entry->d_name, prefix, prefix_len) == 0) {
            snprintf(target_file, sizeof(target_file), "%s/%s", EFIVARS_PATH, entry->d_name);
            break;
        }
    }
    closedir(dir);

    if (target_file[0] == '\0') {
        return -1;
    }

    int fd = open(target_file, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    /* Змінні UEFI містять 4 байти атрибутів (прапорців) на початку файлу */
    uint8_t buffer[12];
    ssize_t bytes_read = read(fd, buffer, sizeof(buffer));
    close(fd);

    if (bytes_read >= 12) {
        /* Атрибути (4 байти) + 64-бітне значення (8 байтів) у форматі little-endian */
        uint64_t val = 0;
        memcpy(&val, buffer + 4, sizeof(uint64_t));
        *out_val = val;
        return 0;
    }

    return -1;
}

/* Розбір параметрів командного рядка ядра з урахуванням екранування */
static int parse_cmdline(BootTelemetry *telem) {
    int fd = open(CMDLINE_PATH, O_RDONLY);
    if (fd < 0) {
        return -1;
    }

    char buffer[4096];
    ssize_t n = read(fd, buffer, sizeof(buffer) - 1);
    close(fd);

    if (n <= 0) {
        return -1;
    }
    buffer[n] = '\0';

    char *token = strtok(buffer, " \t\r\n");
    while (token != NULL) {
        if (strncmp(token, "root=", 5) == 0) {
            strncpy(telem->root_param, token + 5, sizeof(telem->root_param) - 1);
        } else if (strncmp(token, "init=", 5) == 0) {
            strncpy(telem->init_param, token + 5, sizeof(telem->init_param) - 1);
        } else if (strncmp(token, "systemd.unit=", 13) == 0) {
            strncpy(telem->target_unit, token + 13, sizeof(telem->target_unit) - 1);
        }
        token = strtok(NULL, " \t\r\n");
    }

    return 0;
}

/* Зчитування загального часу uptime із ядра */
static double read_uptime_sec(void) {
    FILE *f = fopen(UPTIME_PATH, "r");
    if (!f) {
        return 0.0;
    }

    double uptime = 0.0;
    if (fscanf(f, "%lf", &uptime) != 1) {
        uptime = 0.0;
    }
    fclose(f);
    return uptime;
}

int main(void) {
    BootTelemetry telem;
    memset(&telem, 0, sizeof(telem));
    strcpy(telem.root_param, "не вказано (вбудований)");
    strcpy(telem.init_param, "/sbin/init (типовий)");
    strcpy(telem.target_unit, "default.target");

    printf("====================================================\n");
    printf("    АНАЛІЗАТОР ТЕЛЕМЕТРІЇ ЗАВАНТАЖЕННЯ LINUX        \n");
    printf("====================================================\n\n");

    /* Перевірка режиму завантаження UEFI проти Legacy BIOS */
    struct stat st;
    if (stat(EFIVARS_PATH, &st) == 0 && S_ISDIR(st.st_mode)) {
        telem.is_efi = 1;
        printf("[+] Режим прошивки: UEFI (доступний інтерфейс efivars)\n");

        if (read_efivar_u64("LoaderTimeFirmwareUSec-", &telem.firmware_usec) == 0) {
            printf("    * Час прошивки UEFI (SEC/PEI/DXE): %.3f с\n",
                   (double)telem.firmware_usec / 1000000.0);
        } else {
            printf("    * Час прошивки UEFI: не зафіксовано завантажувачем\n");
        }

        if (read_efivar_u64("LoaderTimeExecUSec-", &telem.loader_usec) == 0) {
            printf("    * Час завантажувача (GRUB/systemd-boot): %.3f с\n",
                   (double)telem.loader_usec / 1000000.0);
        } else {
            printf("    * Час завантажувача: не зафіксовано\n");
        }
    } else {
        telem.is_efi = 0;
        printf("[-] Режим прошивки: Legacy BIOS або efivars не змонтовано\n");
    }

    /* Розбір параметрів старту */
    if (parse_cmdline(&telem) == 0) {
        printf("\n[+] Параметри ядра (/proc/cmdline):\n");
        printf("    * Кореневий пристрій (root):  %s\n", telem.root_param);
        printf("    * Первинний процес (init):    %s\n", telem.init_param);
        printf("    * Цільовий юніт (target):     %s\n", telem.target_unit);
    }

    double current_uptime = read_uptime_sec();
    printf("\n[+] Системний час (Uptime): %.2f с\n", current_uptime);

    printf("\n[+] Оцінка часового бюджету завантаження:\n");
    printf("----------------------------------------------------\n");
    printf(" Етап                      Тривалість      Частка   \n");
    printf("----------------------------------------------------\n");

    double fw_s = (double)telem.firmware_usec / 1000000.0;
    double ld_s = (double)telem.loader_usec / 1000000.0;
    double total_est = fw_s + ld_s + 4.5; /* Оцінка стандартного ядра + userspace */

    if (total_est > 0.0) {
        printf(" Прошивка (Firmware):      %6.3f с        %5.1f%%\n",
               fw_s, (fw_s / total_est) * 100.0);
        printf(" Завантажувач (Loader):    %6.3f с        %5.1f%%\n",
               ld_s, (ld_s / total_est) * 100.0);
        printf(" Ядро + Userspace (оцінка): %6.3f с        %5.1f%%\n",
               4.500, (4.500 / total_est) * 100.0);
    }
    printf("----------------------------------------------------\n");

    return 0;
}
