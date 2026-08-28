/* thread-anatomy.c — що в потоку своє, а що спільне: числами.
   Збірка:  cc -std=c11 -O0 -g -Wall -pthread thread-anatomy.c -o thread-anatomy */
#define _GNU_SOURCE
#include <errno.h>
#include <pthread.h>
#include <semaphore.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>
#ifdef __x86_64__
#include <asm/prctl.h>            /* ARCH_GET_FS */
#endif

#define NWORKERS 3

static int            group_counter;   /* спільна на всю групу задач */
static __thread int   own_counter;     /* своя в кожної задачі */
static __thread pid_t my_tid;          /* хто я — знадобиться в обробнику */

static sem_t quit;                     /* робітникам: час завершуватися */
static sem_t ready;                    /* головній: я вже відзвітував */
static sem_t caught;                   /* головній: сигнал спіймано */
static volatile sig_atomic_t caught_by;

static pid_t tid(void)
{
    return (pid_t) syscall(SYS_gettid);      /* обгортка в glibc лише з 2.30 */
}

static uintptr_t thread_pointer(void)
{
#if defined(__x86_64__)
    uintptr_t tp = 0;
    syscall(SYS_arch_prctl, ARCH_GET_FS, &tp);
    return tp;
#elif defined(__aarch64__)
    uintptr_t tp;
    __asm__ volatile("mrs %0, tpidr_el0" : "=r"(tp));
    return tp;
#else
    return 0;
#endif
}

/* Обробник робить рівно дві дії: запам'ятовує, хто він, і будить головну.
   my_tid читається з блоку ТОГО потоку, у якому виконався обробник. */
static void on_usr1(int sig)
{
    (void) sig;
    caught_by = my_tid;
    sem_post(&caught);
}

static void report(void)
{
    pthread_attr_t attr;
    void  *lo;
    size_t size, guard;
    char   name[16];
    int    on_stack;                     /* адреса цієї змінної — точка в стеку */

    if (pthread_getattr_np(pthread_self(), &attr) != 0)
        return;
    pthread_attr_getstack(&attr, &lo, &size);
    pthread_attr_getguardsize(&attr, &guard);
    pthread_attr_destroy(&attr);
    pthread_getname_np(pthread_self(), name, sizeof name);

    printf("%-8s tid=%-6d getpid()=%d\n", name, (int) my_tid, (int) getpid());
    printf("  стек  [%p .. %p)  %zu КіБ, вартовий %zu Б\n",
           lo, (char *) lo + size, size / 1024, guard);
    printf("  SP    %p — на %td Б нижче від верху ділянки\n",
           (void *) &on_stack, (char *) lo + size - (char *) &on_stack);
    printf("  tp    %#lx   pthread_self() %#lx\n",
           (unsigned long) thread_pointer(), (unsigned long) pthread_self());
    printf("  &own_counter %p   &errno %p   &group_counter %p\n\n",
           (void *) &own_counter, (void *) &errno, (void *) &group_counter);
}

static void *worker(void *arg)
{
    char name[16];

    my_tid = tid();
    own_counter = (int) (intptr_t) arg;
    __atomic_fetch_add(&group_counter, 1, __ATOMIC_RELAXED);
    snprintf(name, sizeof name, "worker-%d", own_counter);
    pthread_setname_np(pthread_self(), name);   /* видно в /proc/<tid>/comm */

    report();
    sem_post(&ready);

    while (sem_wait(&quit) == -1 && errno == EINTR)
        ;                       /* обробник сигналу перериває чекання */
    return NULL;
}

int main(void)
{
    pthread_t w[NWORKERS];
    struct sigaction sa;
    sigset_t usr1;
    int i;

    my_tid = tid();
    own_counter = 100;
    setvbuf(stdout, NULL, _IOLBF, 0);
    sem_init(&quit, 0, 0);
    sem_init(&ready, 0, 0);
    sem_init(&caught, 0, 0);

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_usr1;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGUSR1, &sa, NULL);        /* диспозиція — одна на всю групу */

    pthread_setname_np(pthread_self(), "leader");
    report();

    for (i = 0; i < NWORKERS; i++)
        pthread_create(&w[i], NULL, worker, (void *) (intptr_t) (i + 1));
    for (i = 0; i < NWORKERS; i++)
        sem_wait(&ready);

    /* Маска — властивість ЗАДАЧІ. Робітники успадкували порожню маску
       до цього рядка, тому блокування зачепить лише головну задачу. */
    sigemptyset(&usr1);
    sigaddset(&usr1, SIGUSR1);
    pthread_sigmask(SIG_BLOCK, &usr1, NULL);

    for (i = 0; i < 2; i++) {
        kill(getpid(), SIGUSR1);                  /* адресовано ГРУПІ */
        sem_wait(&caught);
        printf("kill(pid, SIGUSR1)        -> спіймала задача %d\n", (int) caught_by);
    }

    pthread_kill(w[NWORKERS - 1], SIGUSR1);       /* адресовано ЗАДАЧІ */
    sem_wait(&caught);
    printf("pthread_kill(worker-%d)     -> спіймала задача %d\n\n",
           NWORKERS, (int) caught_by);

    printf("pid=%d — подивіться /proc/%d/task/ і натисніть Enter\n",
           (int) getpid(), (int) getpid());
    getchar();

    for (i = 0; i < NWORKERS; i++)
        sem_post(&quit);
    for (i = 0; i < NWORKERS; i++)
        pthread_join(w[i], NULL);

    printf("group_counter=%d (спільний), own_counter головної=%d\n",
           group_counter, own_counter);
    return 0;
}
