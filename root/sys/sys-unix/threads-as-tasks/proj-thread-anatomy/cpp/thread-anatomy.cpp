/* thread-anatomy.cpp — що в потоку своє, а що спільне: числами (C++17).
   Збірка:  g++ -std=c++17 -O0 -g -Wall -pthread thread-anatomy.cpp -o thread-anatomy */
#include <iostream>
#include <thread>
#include <vector>
#include <atomic>
#include <cerrno>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <csignal>
#include <semaphore.h>
#include <pthread.h>
#include <sys/syscall.h>
#include <unistd.h>
#ifdef __x86_64__
#include <asm/prctl.h>
#endif

constexpr int NWORKERS = 3;

static std::atomic<int>      group_counter{0};   /* спільна на всю групу задач */
static thread_local int      own_counter{0};     /* своя в кожної задачі (TLS) */
static thread_local pid_t    my_tid{0};

static sem_t quit;
static sem_t ready;
static sem_t caught;
static volatile sig_atomic_t caught_by;

static pid_t tid()
{
    return static_cast<pid_t>(syscall(SYS_gettid));
}

static uintptr_t thread_pointer()
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

static void on_usr1(int)
{
    caught_by = my_tid;
    sem_post(&caught);
}

static void report()
{
    pthread_attr_t attr;
    void *lo;
    size_t size, guard;
    char name[16];
    int on_stack;

    if (pthread_getattr_np(pthread_self(), &attr) != 0)
        return;
    pthread_attr_getstack(&attr, &lo, &size);
    pthread_attr_getguardsize(&attr, &guard);
    pthread_attr_destroy(&attr);
    pthread_getname_np(pthread_self(), name, sizeof name);

    std::cout << (name[0] ? name : "worker")
              << " tid=" << my_tid << " getpid()=" << getpid() << '\n'
              << "  стек  [" << lo << " .. " << static_cast<void *>(static_cast<char *>(lo) + size) << ") "
              << (size / 1024) << " КіБ, вартовий " << guard << " Б\n"
              << "  SP    " << &on_stack << " — на "
              << (static_cast<char *>(lo) + size - reinterpret_cast<char *>(&on_stack))
              << " Б нижче від верху ділянки\n"
              << "  tp    0x" << std::hex << thread_pointer()
              << "   pthread_self() 0x" << pthread_self() << std::dec << '\n'
              << "  &own_counter " << &own_counter
              << "   &errno " << &errno
              << "   &group_counter " << &group_counter << "\n\n";
}

static void worker_func(int id)
{
    char name[16];
    my_tid = tid();
    own_counter = id;
    group_counter.fetch_add(1, std::memory_order_relaxed);
    snprintf(name, sizeof name, "worker-%d", own_counter);
    pthread_setname_np(pthread_self(), name);

    report();
    sem_post(&ready);

    while (sem_wait(&quit) == -1 && errno == EINTR)
        ;
}

int main()
{
    std::vector<std::thread> workers;
    struct sigaction sa{};
    sigset_t usr1;

    my_tid = tid();
    own_counter = 100;
    std::cout << std::unitbuf;

    sem_init(&quit, 0, 0);
    sem_init(&ready, 0, 0);
    sem_init(&caught, 0, 0);

    sa.sa_handler = on_usr1;
    sigemptyset(&sa.sa_mask);
    sigaction(SIGUSR1, &sa, nullptr);

    pthread_setname_np(pthread_self(), "leader");
    report();

    for (int i = 0; i < NWORKERS; i++)
        workers.emplace_back(worker_func, i + 1);
    for (int i = 0; i < NWORKERS; i++)
        sem_wait(&ready);

    sigemptyset(&usr1);
    sigaddset(&usr1, SIGUSR1);
    pthread_sigmask(SIG_BLOCK, &usr1, nullptr);

    for (int i = 0; i < 2; i++) {
        kill(getpid(), SIGUSR1);
        sem_wait(&caught);
        std::cout << "kill(pid, SIGUSR1)        -> спіймала задача " << caught_by << '\n';
    }

    pthread_kill(workers[NWORKERS - 1].native_handle(), SIGUSR1);
    sem_wait(&caught);
    std::cout << "pthread_kill(worker-" << NWORKERS
              << ")     -> спіймала задача " << caught_by << "\n\n";

    std::cout << "pid=" << getpid() << " — подивіться /proc/" << getpid() << "/task/ і натисніть Enter\n";
    std::cin.get();

    for (int i = 0; i < NWORKERS; i++)
        sem_post(&quit);
    for (auto &w : workers)
        w.join();

    std::cout << "group_counter=" << group_counter
              << " (спільний), own_counter головної=" << own_counter << '\n';
    return 0;
}
