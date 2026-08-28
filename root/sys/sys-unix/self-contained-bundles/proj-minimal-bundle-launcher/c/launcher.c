/* launcher.c — Мінімальний лаунчер пакунка мовою C */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sched.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <errno.h>

#define TARGET_MOUNT_POINT "/tmp/mini_bundle_target"

static int setup_environment(const char *bundle_dir) {
    char new_ld_path[4096];
    char new_bin_path[4096];
    const char *old_ld = getenv("LD_LIBRARY_PATH");
    const char *old_path = getenv("PATH");

    /* Формуємо новий LD_LIBRARY_PATH із пріоритетом усередині пакунка */
    if (old_ld && strlen(old_ld) > 0) {
        snprintf(new_ld_path, sizeof(new_ld_path), "%s/usr/lib:%s", bundle_dir, old_ld);
    } else {
        snprintf(new_ld_path, sizeof(new_ld_path), "%s/usr/lib", bundle_dir);
    }

    if (setenv("LD_LIBRARY_PATH", new_ld_path, 1) != 0) {
        perror("[ERROR] Не вдалося встановити LD_LIBRARY_PATH");
        return -1;
    }

    /* Формуємо новий PATH */
    if (old_path && strlen(old_path) > 0) {
        snprintf(new_bin_path, sizeof(new_bin_path), "%s/usr/bin:%s", bundle_dir, old_path);
    } else {
        snprintf(new_bin_path, sizeof(new_bin_path), "%s/usr/bin", bundle_dir);
    }

    if (setenv("PATH", new_bin_path, 1) != 0) {
        perror("[ERROR] Не вдалося встановити PATH");
        return -1;
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_каталогу_бандла> [аргументи...]\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *bundle_source = argv[1];

    /* Крок 1: Створення приватної копиї простору імен монтажу */
    if (unshare(CLONE_NEWNS) != 0) {
        perror("[ERROR] unshare(CLONE_NEWNS) не вдався (потрібні привілеї CAP_SYS_ADMIN)");
        return EXIT_FAILURE;
    }

    /* Крок 2: Переведення дерева монтажу в режим MS_PRIVATE */
    if (mount(NULL, "/", NULL, MS_PRIVATE | MS_REC, NULL) != 0) {
        perror("[ERROR] Не вдалося змінити режим поширення монтажу на MS_PRIVATE");
        return EXIT_FAILURE;
    }

    /* Крок 3: Створення точки призначення */
    if (mkdir(TARGET_MOUNT_POINT, 0755) != 0 && errno != EEXIST) {
        perror("[ERROR] Не вдалося створити точку монтажу");
        return EXIT_FAILURE;
    }

    /* Крок 4: Виконання bind-mount джерела пакунка в точку призначення */
    if (mount(bundle_source, TARGET_MOUNT_POINT, NULL, MS_BIND | MS_REC, NULL) != 0) {
        perror("[ERROR] bind-mount не вдався");
        return EXIT_FAILURE;
    }

    /* Крок 5: Налаштування змінних середовища */
    if (setup_environment(TARGET_MOUNT_POINT) != 0) {
        return EXIT_FAILURE;
    }

    /* Крок 6: Підготовка аргументів для виконання цільової програми */
    char target_binary[4096];
    snprintf(target_binary, sizeof(target_binary), "%s/usr/bin/app_main", TARGET_MOUNT_POINT);

    char **exec_args = calloc(argc, sizeof(char *));
    if (!exec_args) {
        perror("[ERROR] Помилка виділення пам'яті");
        return EXIT_FAILURE;
    }

    exec_args[0] = target_binary;
    for (int i = 2; i < argc; ++i) {
        exec_args[i - 1] = argv[i];
    }
    exec_args[argc - 1] = NULL;

    printf("[LAUNCHER] Запуск %s всередині ізольованого Mount Namespace...\n", target_binary);

    /* Заміщення образу процесу */
    execv(target_binary, exec_args);

    /* Якщо execv повернув керування — сталася помилка */
    perror("[ERROR] execv не вдався");
    free(exec_args);
    return EXIT_FAILURE;
}
