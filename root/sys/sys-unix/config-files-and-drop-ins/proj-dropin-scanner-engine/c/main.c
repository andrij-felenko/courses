#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/sysmacros.h>
#include <unistd.h>
#include <stdbool.h>

#define MAX_ENTRIES 256
#define MAX_PATH_LEN 1024

/* Рівні пріоритету джерел конфігурації */
typedef enum {
    SOURCE_VENDOR,  /* /usr/lib (Найнижчий пріоритет) */
    SOURCE_RUNTIME, /* /run     (Середній пріоритет) */
    SOURCE_ADMIN    /* /etc     (Найвищий пріоритет) */
} config_tier_t;

/* Запис метаданих знайденого конфігураційного файлу */
typedef struct {
    char filename[256];          /* Базове ім'я файлу (наприклад, 50-net.conf) */
    char full_path[MAX_PATH_LEN];/* Повний абсолютний шлях на диску */
    config_tier_t tier;          /* Джерело походження */
    bool is_masked;              /* Ознака маскування через /dev/null */
} config_file_entry_t;

/* Реєстр зібраних файлів */
typedef struct {
    config_file_entry_t entries[MAX_ENTRIES];
    size_t count;
} config_registry_t;

/*
 * Перевірка маскування:
 * 1. lstat() визначає, чи є файл символьним посиланням.
 * 2. readlink() перевіряє ціль посилання на рівність "/dev/null".
 * 3. stat() перевіряє, чи не є ціль безпосередньо символьним пристроєм (1, 3).
 */
static bool is_path_masked(const char *path) {
    struct stat st;
    if (lstat(path, &st) != 0) {
        return false;
    }

    if (S_ISLNK(st.st_mode)) {
        char target[MAX_PATH_LEN];
        ssize_t len = readlink(path, target, sizeof(target) - 1);
        if (len != -1) {
            target[len] = '\0';
            if (strcmp(target, "/dev/null") == 0 || strcmp(target, "dev/null") == 0) {
                return true;
            }
        }
    }

    if (stat(path, &st) == 0) {
        if (S_ISCHR(st.st_mode) && major(st.st_rdev) == 1 && minor(st.st_rdev) == 3) {
            return true;
        }
    }

    return false;
}

/* Перевірка валідності розширення файлу (.conf) */
static bool has_conf_extension(const char *name) {
    const char *ext = strrchr(name, '.');
    return (ext != NULL && strcmp(ext, ".conf") == 0);
}

/* Компаратор qsort для впорядкування за ASCII-кодами базового імені */
static int compare_entries(const void *a, const void *b) {
    const config_file_entry_t *entry_a = (const config_file_entry_t *)a;
    const config_file_entry_t *entry_b = (const config_file_entry_t *)b;
    return strcmp(entry_a->filename, entry_b->filename);
}

/* Сканування конкретного каталогу ієрархії */
static void scan_directory(const char *dir_path, config_tier_t tier, config_registry_t *reg) {
    DIR *dir = opendir(dir_path);
    if (!dir) {
        return; /* Каталог може бути відсутнім (наприклад, у чистій системі) */
    }

    struct dirent *de;
    while ((de = readdir(dir)) != NULL) {
        /* Ігноруємо поточний каталог '.', батьківський '..' та приховані файли */
        if (de->d_name[0] == '.') {
            continue;
        }

        /* Перевіряємо суворе розширення .conf */
        if (!has_conf_extension(de->d_name)) {
            continue;
        }

        /*
         * Перевірка затінення (Shadowing):
         * Оскільки ми скануємо від вищого пріоритету до нижчого (/etc -> /run -> /usr),
         * якщо базове ім'я вже є в реєстрі, поточний файл відкидається.
         */
        bool already_seen = false;
        for (size_t i = 0; i < reg->count; ++i) {
            if (strcmp(reg->entries[i].filename, de->d_name) == 0) {
                already_seen = true;
                break;
            }
        }

        if (already_seen) {
            continue;
        }

        if (reg->count >= MAX_ENTRIES) {
            fprintf(stderr, "Помилка: перевищено ліміт записів реєстру\\n");
            break;
        }

        config_file_entry_t *entry = &reg->entries[reg->count++];
        snprintf(entry->filename, sizeof(entry->filename), "%s", de->d_name);
        snprintf(entry->full_path, sizeof(entry->full_path), "%s/%s", dir_path, de->d_name);
        entry->tier = tier;
        entry->is_masked = is_path_masked(entry->full_path);
    }

    closedir(dir);
}

int main(int argc, char **argv) {
    const char *subsystem = (argc > 1) ? argv[1] : "sysctl";
    char etc_dir[MAX_PATH_LEN], run_dir[MAX_PATH_LEN], usr_dir[MAX_PATH_LEN];

    snprintf(etc_dir, sizeof(etc_dir), "/etc/%s.d", subsystem);
    snprintf(run_dir, sizeof(run_dir), "/run/%s.d", subsystem);
    snprintf(usr_dir, sizeof(usr_dir), "/usr/lib/%s.d", subsystem);

    config_registry_t registry = { .count = 0 };

    /* 1. Послідовне сканування за спаданням пріоритету для вирішення затінень */
    scan_directory(etc_dir, SOURCE_ADMIN, &registry);
    scan_directory(run_dir, SOURCE_RUNTIME, &registry);
    scan_directory(usr_dir, SOURCE_VENDOR, &registry);

    /* 2. Лексикографічне сортування результуючого набору за ASCII */
    qsort(registry.entries, registry.count, sizeof(config_file_entry_t), compare_entries);

    /* 3. Генерація підсумкового плану виконання */
    printf("=== ПЛАН ЗАВАНТАЖЕННЯ КОНФІГУРАЦІЇ ДЛЯ [%s.d] ===\\n", subsystem);
    for (size_t i = 0; i < registry.count; ++i) {
        config_file_entry_t *e = &registry.entries[i];
        const char *tier_str = (e->tier == SOURCE_ADMIN) ? "[ADMIN /etc]" :
                               (e->tier == SOURCE_RUNTIME) ? "[RUN /run]" : "[VENDOR /usr]";

        if (e->is_masked) {
            printf("  [-] %-22s -> %-40s %s (ЗАМАСКОВАНО /dev/null)\\n",
                   e->filename, e->full_path, tier_str);
        } else {
            printf("  [+] %-22s -> %-40s %s\\n",
                   e->filename, e->full_path, tier_str);
        }
    }

    return 0;
}
