#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

// ── Одиниця роботи (одна задача, важить ~1 секунду) ────────────────────
// I/O-задача: секунда СНУ. nanosleep знімає потік із черги готових і зводить
// таймер — ядро на цей час вільне, точнісінько як на мережевому чеканні.
static void io_one(void) {
    struct timespec req = {1, 0};      // 1 секунда, 0 наносекунд
    nanosleep(&req, NULL);
}

// CPU-задача: секунда СПРАВЖНЬОЇ лічби. Тіло — крок LCG (x = x·a + c): ланцюг
// залежних множень, який компілятор НЕ згорне у формулу (просту суму n він
// звів би за Гаусом і зміряв нуль). Атомарний blackhole не дає ні викинути
// результат, ні влаштувати гонку двох потоків. N підбери під свою машину.
_Atomic unsigned long long blackhole;

static void cpu_one(void) {
    unsigned long long x = 0x9e3779b97f4a7c15ULL;
    for (unsigned long long n = 0; n < 1000000000ULL; n++)
        x = x * 6364136223846793005ULL + 1442695040888963407ULL;
    blackhole += x;                    // атомарний RMW — і лічбу видно, і гонки нема
}

// ── Режими: як прогнати ДВІ такі задачі ────────────────────────────────
typedef void (*task_fn)(void);

static void sequential(task_fn task) { task(); task(); } // одна за одною → нуль відліку

static void *worker(void *arg) {
    task_fn task = *(task_fn *)arg;    // arg вказує на змінну task із concurrent
    task();
    return NULL;
}

static void concurrent(task_fn task) { // два СПРАВЖНІ потоки ОС — без GIL і без рантайму
    pthread_t th[2];
    for (int i = 0; i < 2; i++)
        pthread_create(&th[i], NULL, worker, &task);
    for (int i = 0; i < 2; i++)
        pthread_join(th[i], NULL);
}

// ── Важіль: на скільки ЯДЕР пускати потоки (афінність процесу) ──────────
// Потоки успадковують маску творця, тож ставимо її ДО concurrent. Це найнижчий,
// «залізний» важіль — те, що GOMAXPROCS і вибір потік/процес лише вдягають
// зверху. Linux-специфіка; на macOS/Windows та сама ідея зветься інакше.
static void pin_to_cores(int n) {
    cpu_set_t set;
    CPU_ZERO(&set);
    for (int i = 0; i < n; i++)
        CPU_SET(i, &set);
    sched_setaffinity(0, sizeof(set), &set);
}

// ── Секундомір: розігрів + найменший із кількох прогонів (менше шуму) ───
static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);   // календарний (стінний) монотонний час
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void timeit(const char *label, void (*run)(task_fn), task_fn task) {
    run(task);                     // РОЗІГРІВ — перший прогін не міряємо
    double best = 0;
    for (int i = 0; i < 3; i++) {
        double t0 = now_sec();
        run(task);
        double d = now_sec() - t0;
        if (i == 0 || d < best) best = d;
    }
    printf("%-30s %.2fs\n", label, best);
}

int main(void) {
    printf("ядер у машині: %ld\n", sysconf(_SC_NPROCESSORS_ONLN));

    pin_to_cores(1); // навмисно ОДНЕ ядро
    timeit("I/O · послідовно",           sequential, io_one);  // ≈ 2.00s
    timeit("I/O · конкурентно (1 ядро)", concurrent, io_one);  // ≈ 1.00s
    timeit("CPU · послідовно",           sequential, cpu_one); // ≈ 2.00s
    timeit("CPU · конкурентно (1 ядро)", concurrent, cpu_one); // ≈ 2.00s

    pin_to_cores(2); // тепер дозволяємо двом ядрам працювати водночас
    timeit("I/O · паралельно (2 ядра)",  concurrent, io_one);  // ≈ 1.00s — дарма
    timeit("CPU · паралельно (2 ядра)",  concurrent, cpu_one); // ≈ 1.00s — виграш
    return 0;
}
