#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
#include <asm/prctl.h>
#include <sys/prctl.h>
#include <unistd.h>

int arch_prctl(int code, unsigned long *addr);

/* Оголошення TLS-змінних з різними специфікованими моделями доступу */
__thread int global_tls_var = 100;
__attribute__((tls_model("local-exec"))) __thread int le_tls_var = 200;
__attribute__((tls_model("initial-exec"))) __thread int ie_tls_var = 300;

void print_tls_info(const char *thread_name) {
    uintptr_t fs_base = 0;
    uintptr_t fs_syscall = 0;
    
    /* Зчитування значення self-pointer з FS:0 за допомогою асемблерної вставки */
#if defined(__x86_64__)
    __asm__ __volatile__("mov %%fs:0, %0" : "=r"(fs_base));
#endif

    /* Альтернативне зчитування через системний виклик arch_prctl */
    arch_prctl(ARCH_GET_FS, &fs_syscall);

    printf("=== [%s] (ID потоку: %lu) ===\n", thread_name, (unsigned long)pthread_self());
    printf("  Базова адреса FS (з FS:0): 0x%lx\n", (unsigned long)fs_base);
    printf("  Базова адреса FS (з syscall): 0x%lx\n", (unsigned long)fs_syscall);
    
    /* Обчислення від'ємних або позитивних зміщень у байтах */
    intptr_t off_global = (char*)&global_tls_var - (char*)fs_base;
    intptr_t off_le     = (char*)&le_tls_var - (char*)fs_base;
    intptr_t off_ie     = (char*)&ie_tls_var - (char*)fs_base;

    printf("  &global_tls_var: 0x%p | зміщення від FS: %ld байтів\n", (void*)&global_tls_var, (long)off_global);
    printf("  &le_tls_var:     0x%p | зміщення від FS: %ld байтів\n", (void*)&le_tls_var, (long)off_le);
    printf("  &ie_tls_var:     0x%p | зміщення від FS: %ld байтів\n", (void*)&ie_tls_var, (long)off_ie);
    printf("\n");
}

void* worker_thread(void* arg) {
    print_tls_info((const char*)arg);
    return NULL;
}

int main(void) {
    pthread_t thread1, thread2;

    print_tls_info("Головний потік (Main)");

    pthread_create(&thread1, NULL, worker_thread, "Робочий потік 1");
    pthread_create(&thread2, NULL, worker_thread, "Робочий потік 2");

    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);

    return 0;
}
