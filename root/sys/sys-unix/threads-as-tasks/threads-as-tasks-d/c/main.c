#define _GNU_SOURCE
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>

static void *worker(void *arg)
{
    (void)arg;
    printf("потік:   getpid()=%d  gettid()=%ld\n",
           getpid(), (long)syscall(SYS_gettid));
    return NULL;
}

int main(void)
{
    pthread_t t;
    printf("головний: getpid()=%d  gettid()=%ld\n",
           getpid(), (long)syscall(SYS_gettid));
    pthread_create(&t, NULL, worker, NULL);
    pthread_join(t, NULL);
    return 0;
}
