#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdatomic.h>
#include <sys/stat.h>
#include <sys/types.h>

#define WORK_DIR "/tmp/toctou_test_c"
#define TARGET_PATH WORK_DIR "/vulnerable_file.txt"
#define SECRET_PATH WORK_DIR "/canary_secret.txt"
#define ITERATIONS 50000

static atomic_bool g_running = 1;
static atomic_long g_exploited_count = 0;
static atomic_long g_victim_attempts = 0;

void* attacker_thread(void* arg) {
    (void)arg;
    char temp_real[256];
    char temp_sym[256];
    snprintf(temp_real, sizeof(temp_real), "%s/tmp_real", WORK_DIR);
    snprintf(temp_sym, sizeof(temp_sym), "%s/tmp_sym", WORK_DIR);

    while (atomic_load(&g_running)) {
        // Створюємо справжній файл і симлінк на секрет
        int fd = open(temp_real, O_WRONLY | O_CREAT | O_TRUNC, 0600);
        if (fd >= 0) close(fd);
        unlink(temp_sym);
        symlink(SECRET_PATH, temp_sym);

        // Швидко перемикаємо TARGET_PATH між реальним файлом і симлінком
        rename(temp_real, TARGET_PATH);
        rename(temp_sym, TARGET_PATH);
    }
    return NULL;
}

void* vulnerable_victim_thread(void* arg) {
    (void)arg;
    for (long i = 0; i < ITERATIONS; ++i) {
        atomic_fetch_add(&g_victim_attempts, 1);

        // 1. ЕТАП ПЕРЕВІРКИ (TOC): перевіряємо, чи файл існує і доступний
        if (access(TARGET_PATH, F_OK | W_OK) == 0) {
            // Симуляція внутрішньої обробки або перемикання контексту ядра
            usleep(1);

            // 2. ЕТАП ВИКОРИСТАННЯ (TOU): відкриваємо файл за текстовим шляхом
            int fd = open(TARGET_PATH, O_WRONLY);
            if (fd >= 0) {
                const char msg[] = "CORRUPTED_BY_VICTIM\n";
                write(fd, msg, sizeof(msg) - 1);
                close(fd);
            }
        }
    }
    atomic_store(&g_running, 0);
    return NULL;
}

int main(void) {
    mkdir(WORK_DIR, 0700);

    // Створюємо захищений файл-пастку
    int sfd = open(SECRET_PATH, O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (sfd >= 0) {
        const char initial[] = "ORIGINAL_SECRET_STATE\n";
        write(sfd, initial, sizeof(initial) - 1);
        close(sfd);
    }

    pthread_t th_att, th_vic;
    pthread_create(&th_att, NULL, attacker_thread, NULL);
    pthread_create(&th_vic, NULL, vulnerable_victim_thread, NULL);

    pthread_join(th_vic, NULL);
    pthread_join(th_att, NULL);

    // Перевіряємо цілісність секретного файлу
    char buf[128] = {0};
    int rfd = open(SECRET_PATH, O_RDONLY);
    if (rfd >= 0) {
        read(rfd, buf, sizeof(buf) - 1);
        close(rfd);
    }

    printf("=== Результати вразливої схеми ===\n");
    printf("Спроб жертви: %ld\n", atomic_load(&g_victim_attempts));
    printf("Вміст canary-файлу: %s", buf);

    if (strstr(buf, "CORRUPTED_BY_VICTIM")) {
        printf("СТАТУС: ВРАЗЛИВІСТЬ ПІДТВЕРДЖЕНО (секрет пошкоджено через TOCTOU!)\n");
    } else {
        printf("СТАТУС: Гонка не спрацювала в цій серії спроб.\n");
    }

    unlink(TARGET_PATH);
    unlink(SECRET_PATH);
    rmdir(WORK_DIR);
    return 0;
}
