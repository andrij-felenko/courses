/* dac_probe.c — Покроковий симулятор перевірки прав VFS ядра Linux на C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <pwd.h>
#include <grp.h>

typedef struct {
    uid_t uid, euid, suid, fsuid;
    gid_t gid, egid, sgid, fsgid;
    int ngroups;
    gid_t *groups;
} ProcessCreds;

/* Завантаження облікових даних поточного процесу */
int load_credentials(ProcessCreds *creds) {
    if (getresuid(&creds->uid, &creds->euid, &creds->suid) != 0 ||
        getresgid(&creds->gid, &creds->egid, &creds->sgid) != 0) {
        return -1;
    }
    creds->fsuid = creds->euid;
    creds->fsgid = creds->egid;

    creds->ngroups = getgroups(0, NULL);
    if (creds->ngroups > 0) {
        creds->groups = malloc(sizeof(gid_t) * creds->ngroups);
        if (!creds->groups || getgroups(creds->ngroups, creds->groups) < 0) {
            free(creds->groups);
            creds->groups = NULL;
            creds->ngroups = 0;
        }
    } else {
        creds->groups = NULL;
    }
    return 0;
}

void free_credentials(ProcessCreds *creds) {
    if (creds->groups) {
        free(creds->groups);
        creds->groups = NULL;
    }
}

/* Перевірка входження цільового GID у список груп процесу */
int in_group_list(const ProcessCreds *c, gid_t target_gid) {
    if (c->fsgid == target_gid) return 1;
    for (int i = 0; i < c->ngroups; ++i) {
        if (c->groups[i] == target_gid) return 1;
    }
    return 0;
}

/* Емуляція generic_permission для одного конкретного inode */
int evaluate_inode_dac(const ProcessCreds *c, const struct stat *st, int req_r, int req_w, int req_x, const char **matched_class) {
    int mode = st->st_mode;

    /* 1. Клас Власника */
    if (c->fsuid == st->st_uid) {
        *matched_class = "ВЛАСНИК (Owner)";
        if (req_r && !(mode & S_IRUSR)) return 0;
        if (req_w && !(mode & S_IWUSR)) return 0;
        if (req_x && !(mode & S_IXUSR)) return 0;
        return 1;
    }

    /* 2. Клас Групи */
    if (in_group_list(c, st->st_gid)) {
        *matched_class = "ГРУПА (Group)";
        if (req_r && !(mode & S_IRGRP)) return 0;
        if (req_w && !(mode & S_IWGRP)) return 0;
        if (req_x && !(mode & S_IXGRP)) return 0;
        return 1;
    }

    /* 3. Клас Інших користувачів */
    *matched_class = "РЕШТА (Others)";
    if (req_r && !(mode & S_IROTH)) return 0;
    if (req_w && !(mode & S_IWOTH)) return 0;
    if (req_x && !(mode & S_IXOTH)) return 0;
    return 1;
}

void probe_path(const char *target_path, int req_r, int req_w, int req_x) {
    ProcessCreds creds;
    if (load_credentials(&creds) != 0) {
        fprintf(stderr, "Помилка читання облікових даних процесу\n");
        return;
    }

    printf("========================================================\n");
    printf("ДІАГНОСТИКА ДОСТУПУ ДО: %s\n", target_path);
    printf("Ідентичність: fsuid=%u, fsgid=%u, додаткових груп=%d\n", creds.fsuid, creds.fsgid, creds.ngroups);
    printf("Запитувані права: Read=%d, Write=%d, Exec/Search=%d\n", req_r, req_w, req_x);
    printf("========================================================\n\n");

    /* Перевірка стану точки монтування */
    struct statvfs vfs;
    if (statvfs(target_path, &vfs) == 0) {
        if ((vfs.f_flag & ST_RDONLY) && req_w) {
            printf("[ПОПЕРЕДЖЕННЯ] Точка монтування перебуває в режимі READ-ONLY (EROFS)!\n\n");
        }
    }

    /* Канонізація цільового шляху */
    char resolved[4096];
    if (!realpath(target_path, resolved)) {
        strncpy(resolved, target_path, sizeof(resolved) - 1);
        resolved[sizeof(resolved) - 1] = '\0';
    }

    /* Фаза 1: Покомпонентний прохід деревом каталогів */
    printf("ФАЗА 1: Покомпонентний обхід шляху (link_path_walk):\n");
    char temp_path[4096];
    char *cursor = resolved;
    int depth = 0;
    int traversal_ok = 1;

    while (*cursor) {
        if (*cursor == '/') {
            cursor++;
            continue;
        }
        char *slash = strchr(cursor, '/');
        if (!slash) {
            /* Дійшли до кінцевого об'єкта */
            break;
        }

        size_t len = slash - resolved;
        if (len >= sizeof(temp_path)) len = sizeof(temp_path) - 1;
        strncpy(temp_path, resolved, len);
        temp_path[len] = '\0';
        if (len == 0) strcpy(temp_path, "/");

        struct stat st;
        if (stat(temp_path, &st) != 0) {
            printf("  [%d] Каталог '%s' -> НЕ ЗНАЙДЕНО (%s)\n", depth, temp_path, strerror(errno));
            traversal_ok = 0;
            break;
        }

        const char *mclass = NULL;
        int can_search = evaluate_inode_dac(&creds, &st, 0, 0, 1, &mclass);
        printf("  [%d] Каталог '%s' (mode=%04o, uid=%u, gid=%u)\n", depth, temp_path, st.st_mode & 07777, st.st_uid, st.st_gid);
        printf("      Збіг: %s -> Пошук (+x): %s\n", mclass, can_search ? "ДОЗВОЛЕНО" : "ВІДМОВА [EACCES]");

        if (!can_search) {
            printf("\n>>> КРИТИЧНА ПОМИЛКА: Ядро перериває обхід на каталозі '%s'!\n", temp_path);
            printf(">>> Причина: брак біта +x у класі '%s'. Кінцевий файл недосяжний.\n", mclass);
            traversal_ok = 0;
            break;
        }

        cursor = slash + 1;
        depth++;
    }

    if (!traversal_ok) {
        free_credentials(&creds);
        return;
    }

    /* Фаза 2: Перевірка цільового об'єкта */
    printf("\nФАЗА 2: Перевірка прав цільового об'єкта:\n");
    struct stat target_st;
    if (stat(resolved, &target_st) != 0) {
        if (errno == ENOENT) {
            printf("  Файл '%s' ще не існує.\n", resolved);
            if (req_w) {
                printf("  Для створення файлу потрібні права на запис (+w) у батьківському каталозі.\n");
            }
        } else {
            printf("  Помилка доступу до '%s': %s\n", resolved, strerror(errno));
        }
        free_credentials(&creds);
        return;
    }

    const char *target_class = NULL;
    int target_access = evaluate_inode_dac(&creds, &target_st, req_r, req_w, req_x, &target_class);

    printf("  Цільовий об'єкт: '%s'\n", resolved);
    printf("  Тип: %s, Режим: %04o, Власник: %u:%u\n",
           S_ISDIR(target_st.st_mode) ? "Каталог" : S_ISREG(target_st.st_mode) ? "Звичайний файл" : "Інше",
           target_st.st_mode & 07777, target_st.st_uid, target_st.st_gid);
    printf("  Збіг класу: %s\n", target_class);
    printf("  Результат перевірки DAC: %s\n\n", target_access ? "ДОСТУП ДОЗВОЛЕНО" : "ВІДМОВА [EACCES]");

    if (!target_access) {
        printf(">>> ПРИЧИНА ВІДМОВИ:\n");
        printf(">>> Запитувана операція відсутня в обраній трійці прав (%s).\n", target_class);
        printf(">>> Пам'ятайте: класи є взаємовиключними, права інших категорій не додаються!\n");
    }

    free_credentials(&creds);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях> [r] [w] [x]\n", argv[0]);
        fprintf(stderr, "Приклад: %s /var/log/app/service.log r w\n", argv[0]);
        return 1;
    }

    int req_r = 0, req_w = 0, req_x = 0;
    if (argc == 2) {
        req_r = 1;
    } else {
        for (int i = 2; i < argc; ++i) {
            if (strchr(argv[i], 'r')) req_r = 1;
            if (strchr(argv[i], 'w')) req_w = 1;
            if (strchr(argv[i], 'x')) req_x = 1;
        }
    }

    probe_path(argv[1], req_r, req_w, req_x);
    return 0;
}
