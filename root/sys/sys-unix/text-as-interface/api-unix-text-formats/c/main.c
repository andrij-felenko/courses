#define _GNU_SOURCE
#include <pwd.h>
#include <stdio.h>
#include <mntent.h>
#include <string.h>

// Порядкова ітерація через /etc/passwd за допомогою POSIX getpwent()
void print_regular_users(void) {
    struct passwd *pw;
    setpwent(); // Перемотування файлу облікових записів на початок
    while ((pw = getpwent()) != NULL) {
        if (pw->pw_uid >= 1000) {
            printf("Користувач: %s, UID: %u, Оболонка: %s\n",
                   pw->pw_name, (unsigned int)pw->pw_uid, pw->pw_shell);
        }
    }
    endpwent(); // Закриття файлового дескриптора
}

// Порядкове читання монтувань ядра через mntent
void list_ext4_mounts(void) {
    FILE *fp = setmntent("/proc/mounts", "r");
    if (!fp) return;

    struct mntent *ent;
    while ((ent = getmntent(fp)) != NULL) {
        if (strcmp(ent->mnt_type, "ext4") == 0) {
            printf("Пристрій: %s -> Точка монтування: %s\n",
                   ent->mnt_fsname, ent->mnt_dir);
        }
    }
    endmntent(fp);
}
