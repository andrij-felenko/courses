/* target_app.c - Цільова програма мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

/* Функція, затримку якої ми будемо інструментувати */
void compute_hash(int iterations) {
    volatile long long hash = 0;
    for (int i = 0; i < iterations * 100000; i++) {
        hash += i ^ (i >> 3);
    }
}

int main(int argc, char **argv) {
    printf("Target App C запущено (PID: %d)\n", getpid());
    while (1) {
        compute_hash(50);
        usleep(500000); /* 500 мс пауза */
        compute_hash(200);
        usleep(500000);
    }
    return 0;
}
