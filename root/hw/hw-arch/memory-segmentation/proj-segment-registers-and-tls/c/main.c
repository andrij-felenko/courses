#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <asm/prctl.h>
#include <sys/prctl.h>

/* Оголошення системного виклику arch_prctl для архітектури x86-64 */
int arch_prctl(int code, unsigned long addr);

/* Локальні змінні потоку (Thread-Local Storage) */
static __thread uint64_t tls_counter = 0x1122334455667788ULL;
static __thread char     tls_buffer[64] = "Потік-локальний буфер даних";

/* Читання поточної 64-бітної базової адреси сегмента FS через ядро */
static uint64_t get_fs_base_syscall(void) {
    unsigned long fs_base = 0;
    if (syscall(SYS_arch_prctl, ARCH_GET_FS, &fs_base) == 0) {
        return (uint64_t)fs_base;
    }
    return 0;
}

/* Пряме читання FS_BASE через асемблерну інструкцію самопокажчика glibc */
static inline uint64_t get_fs_self_pointer(void) {
    uint64_t self_ptr = 0;
    __asm__ volatile("movq %%fs:0x0, %0" : "=r"(self_ptr));
    return self_ptr;
}

/* Пряме читання значення Stack Canary з регістра fs:0x28 */
static inline uint64_t get_stack_canary_from_fs(void) {
    uint64_t canary = 0;
    __asm__ volatile("movq %%fs:0x28, %0" : "=r"(canary));
    return canary;
}

static void *thread_worker(void *arg) {
    int thread_id = *(int *)arg;
    
    uint64_t fs_base = get_fs_base_syscall();
    uint64_t fs_self = get_fs_self_pointer();
    uint64_t canary  = get_stack_canary_from_fs();
    
    printf("\n[Потік %d]\n", thread_id);
    printf("  FS_BASE (через arch_prctl) : 0x%016lx\n", fs_base);
    printf("  Покажчик на себе (fs:0x0)  : 0x%016lx\n", fs_self);
    printf("  Stack Canary (fs:0x28)     : 0x%016lx\n", canary);
    printf("  Адреса змінної tls_counter : %p (зсув від FS: %ld байтів)\n",
           (void *)&tls_counter, (int64_t)((uintptr_t)&tls_counter - fs_base));
    printf("  Адреса буфера tls_buffer   : %p (зсув від FS: %ld байтів)\n",
           (void *)tls_buffer, (int64_t)((uintptr_t)tls_buffer - fs_base));
    
    return NULL;
}

int main(void) {
    printf("=== Дослідження сегментації x86-64 та регістра FS ===\n");
    
    int id_main = 0;
    thread_worker(&id_main);
    
    pthread_t th1, th2;
    int id1 = 1, id2 = 2;
    
    pthread_create(&th1, NULL, thread_worker, &id1);
    pthread_create(&th2, NULL, thread_worker, &id2);
    
    pthread_join(th1, NULL);
    pthread_join(th2, NULL);
    
    return 0;
}
