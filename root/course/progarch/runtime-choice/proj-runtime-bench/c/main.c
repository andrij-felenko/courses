// C + pthreads: один потік ОС на кожне сонне з'єднання — стек як стіна
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/socket.h>

static void *hold(void *arg) {
    int fd = (int)(intptr_t)arg;
    char b;
    read(fd, &b, 1);                  // блокує НАЗАВЖДИ — з'єднання «спить»
    return NULL;
}

static long stat_mb(const char *field) {      // поле з /proc/self/status, КБ → МБ
    FILE *f = fopen("/proc/self/status", "r");
    char line[256];
    long kb = -1;
    while (fgets(line, sizeof line, f))
        if (strncmp(line, field, strlen(field)) == 0) {
            sscanf(line + strlen(field), "%ld", &kb);
            break;
        }
    fclose(f);
    return kb / 1024;
}

int main(int argc, char **argv) {
    int N = argc > 1 ? atoi(argv[1]) : 2000;
    int *keep = malloc(sizeof(int) * 2 * N);   // тримаємо обидва кінці, щоб не закрились
    int i;
    for (i = 0; i < N; i++) {
        int sv[2];
        socketpair(AF_UNIX, SOCK_STREAM, 0, sv);
        keep[2*i] = sv[0];
        keep[2*i + 1] = sv[1];
        pthread_t t;
        // стек за замовчуванням — 8 МБ на КОЖЕН потік (зменшує pthread_attr_setstacksize)
        if (pthread_create(&t, NULL, hold, (void *)(intptr_t)sv[0]) != 0) {
            fprintf(stderr, "стоп на %d-му: pthread_create → стіна лічильника\n", i);
            break;                              // упремося в TasksMax/map_count задовго до RAM
        }
        pthread_detach(t);
    }
    usleep(500000);                             // дати потокам осісти на read()
    printf("%d потоків:  VmRSS≈%ld МБ   VmSize≈%ld МБ\n",
           i, stat_mb("VmRSS:"), stat_mb("VmSize:"));
    return 0;
}
// gcc hold.c -lpthread ; N=2000 → VmSize +~16 ГБ (2000×8 МБ віртуально), VmRSS — десятки МБ.
// Підніми N до десятків тисяч — pthread_create кине EAGAIN: та сама стіна, що й у Python.
