/* loader.c — C імплементація з використанням libbpf */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <bpf/libbpf.h>
#include "block_chmod.skel.h"

int main(int argc, char **argv)
{
    struct block_chmod_bpf *skel;
    int err;

    // 1. Відкриваємо BPF-скелет
    skel = block_chmod_bpf__open();
    if (!skel) {
        fprintf(stderr, "Failed to open BPF skeleton\n");
        return 1;
    }

    // 2. Завантажуємо та верифікуємо BPF-програму в ядрі
    err = block_chmod_bpf__load(skel);
    if (err) {
        fprintf(stderr, "Failed to load BPF program: %d\n", err);
        goto cleanup;
    }

    // 3. Прикріплюємо програму до LSM-хука
    err = block_chmod_bpf__attach(skel);
    if (err) {
        fprintf(stderr, "Failed to attach BPF LSM program: %d\n", err);
        goto cleanup;
    }

    printf("BPF-LSM Policy active! Non-root users cannot run 'chmod'.\n");
    printf("Press Ctrl+C to unload policy and exit.\n");

    while (1) {
        sleep(1);
    }

cleanup:
    block_chmod_bpf__destroy(skel);
    return -err;
}
