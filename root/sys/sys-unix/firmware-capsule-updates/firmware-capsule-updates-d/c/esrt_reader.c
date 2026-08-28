/* esrt_reader.c — Читання атрибутів ESRT мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <fcntl.h>

#define ESRT_PATH "/sys/firmware/efi/esrt/entries"

static void read_sysfs_string(const char *dir_path, const char *file_name, char *buffer, size_t max_len) {
    char full_path[512];
    snprintf(full_path, sizeof(full_path), "%s/%s", dir_path, file_name);
    
    int fd = open(full_path, O_RDONLY);
    if (fd < 0) {
        strncpy(buffer, "N/A", max_len);
        return;
    }
    
    ssize_t bytes_read = read(fd, buffer, max_len - 1);
    close(fd);
    
    if (bytes_read > 0) {
        buffer[bytes_read] = '\0';
        char *newline = strchr(buffer, '\n');
        if (newline) *newline = '\0';
    } else {
        strncpy(buffer, "N/A", max_len);
    }
}

static unsigned int read_sysfs_uint(const char *dir_path, const char *file_name) {
    char buf[64];
    read_sysfs_string(dir_path, file_name, buf, sizeof(buf));
    return (unsigned int)strtoul(buf, NULL, 0);
}

const char* decode_esrt_status(unsigned int status) {
    switch (status) {
        case 0: return "Успішно (Success)";
        case 1: return "Помилка (Unsuccessful)";
        case 2: return "Недостатньо ресурсів (Insufficient Resources)";
        case 3: return "Некоректна версія / Anti-Rollback (Incorrect Version)";
        case 4: return "Невірний формат капсули (Invalid Format)";
        case 5: return "Помилка автентифікації підпису (Auth Error)";
        case 6: return "Відсутнє живлення від мережі AC (Power Event)";
        default: return "Невідомий код помилки";
    }
}

int main(void) {
    DIR *dir = opendir(ESRT_PATH);
    if (!dir) {
        perror("Не вдалося відкрити " ESRT_PATH " (UEFI ESRT не підтримується або відсутній)");
        return EXIT_FAILURE;
    }

    struct dirent *entry;
    printf("%-38s | %-10s | %-10s | %s\n", "GUID пристрою (FwClass)", "Версія", "Остання", "Статус останньої спроби");
    printf("--------------------------------------------------------------------------------------------------------\n");

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') continue;

        char entry_dir[512];
        snprintf(entry_dir, sizeof(entry_dir), "%s/%s", ESRT_PATH, entry->d_name);

        char fw_class[64];
        read_sysfs_string(entry_dir, "fw_class", fw_class, sizeof(fw_class));

        unsigned int fw_version = read_sysfs_uint(entry_dir, "fw_version");
        unsigned int last_version = read_sysfs_uint(entry_dir, "last_attempt_version");
        unsigned int last_status = read_sysfs_uint(entry_dir, "last_attempt_status");

        printf("%-38s | 0x%-8X | 0x%-8X | %s\n",
               fw_class, fw_version, last_version, decode_esrt_status(last_status));
    }

    closedir(dir);
    return EXIT_SUCCESS;
}
