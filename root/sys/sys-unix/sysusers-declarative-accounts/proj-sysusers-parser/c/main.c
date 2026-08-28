#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <shadow.h>
#include <pwd.h>
#include <grp.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <errno.h>

#define SYS_UID_MIN 100
#define SYS_UID_MAX 999

typedef struct {
    char type;
    char name[32];
    uid_t requested_uid;
    char comment[64];
    char home[128];
    char shell[64];
} sysuser_rule_t;

/* Перевірка чи існує ім'я або UID у поточній базі passwd */
static int user_exists(const char *name, uid_t uid) {
    struct passwd *pw;
    setpwent();
    while ((pw = getpwent()) != NULL) {
        if (strcmp(pw->pw_name, name) == 0 || (uid != 0 && pw->pw_uid == uid)) {
            endpwent();
            return 1;
        }
    }
    endpwent();
    return 0;
}

/* Пошук першого вільного UID у системному діапазоні SYS_UID_MIN..SYS_UID_MAX */
static uid_t find_free_uid(void) {
    for (uid_t candidate = SYS_UID_MIN; candidate <= SYS_UID_MAX; candidate++) {
        int used = 0;
        struct passwd *pw;
        setpwent();
        while ((pw = getpwent()) != NULL) {
            if (pw->pw_uid == candidate) {
                used = 1;
                break;
            }
        }
        endpwent();
        if (!used) {
            return candidate;
        }
    }
    return 0;
}

/* Атомарне додавання запису користувача у /etc/passwd */
int add_sysuser(const sysuser_rule_t *rule) {
    if (lckpwdf() != 0) {
        fprintf(stderr, "Помилка блокування бази даних passwd: %s\n", strerror(errno));
        return -1;
    }

    if (user_exists(rule->name, rule->requested_uid)) {
        printf("Користувач %s або UID %u вже існує. Пропускаємо.\n", rule->name, rule->requested_uid);
        ulckpwdf();
        return 0;
    }

    uid_t final_uid = rule->requested_uid;
    if (final_uid == 0) {
        final_uid = find_free_uid();
        if (final_uid == 0) {
            fprintf(stderr, "Немає вільних UID у діапазоні %d-%d\n", SYS_UID_MIN, SYS_UID_MAX);
            ulckpwdf();
            return -1;
        }
    }

    /* Відкриваємо існуючий /etc/passwd та створюємо /etc/passwd.tmp */
    FILE *old_fp = fopen("/etc/passwd", "r");
    if (!old_fp) {
        perror("Помилка відкриття /etc/passwd");
        ulckpwdf();
        return -1;
    }

    int tmp_fd = open("/etc/passwd.tmp", O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (tmp_fd < 0) {
        perror("Помилка створення /etc/passwd.tmp");
        fclose(old_fp);
        ulckpwdf();
        return -1;
    }

    FILE *tmp_fp = fdopen(tmp_fd, "w");
    if (!tmp_fp) {
        perror("fdopen помилка");
        close(tmp_fd);
        fclose(old_fp);
        ulckpwdf();
        return -1;
    }

    /* Копіюємо наявні записи */
    char buffer[1024];
    while (fgets(buffer, sizeof(buffer), old_fp)) {
        fputs(buffer, tmp_fp);
    }
    fclose(old_fp);

    /* Записуємо новий рядок користувача */
    fprintf(tmp_fp, "%s:x:%u:%u:%s:%s:%s\n",
            rule->name,
            final_uid,
            final_uid, /* GID дорівнює UID */
            rule->comment[0] ? rule->comment : rule->name,
            rule->home[0] ? rule->home : "/",
            rule->shell[0] ? rule->shell : "/usr/sbin/nologin");

    fflush(tmp_fp);
    if (fsync(fileno(tmp_fp)) != 0) {
        perror("Помилка скидання даних на диск (fsync)");
        fclose(tmp_fp);
        unlink("/etc/passwd.tmp");
        ulckpwdf();
        return -1;
    }
    fclose(tmp_fp);

    /* Атомарна заміна файлу */
    if (rename("/etc/passwd.tmp", "/etc/passwd") != 0) {
        perror("Помилка атомарної заміни rename()");
        unlink("/etc/passwd.tmp");
        ulckpwdf();
        return -1;
    }

    ulckpwdf();
    printf("Успішно додано користувача %s (UID: %u)\n", rule->name, final_uid);
    return 0;
}
