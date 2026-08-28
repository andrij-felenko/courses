#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/wait.h>

#define ARRAY_SIZE 1000000

// Структура для передачі завдань потоку
typedef struct {
    const int *data;
    size_t start;
    size_t end;
    long long partial_sum;
} ThreadTask;

static void *thread_worker(void *arg) {
    ThreadTask *task = (ThreadTask *)arg;
    long long sum = 0;
    for (size_t i = task->start; i < task->end; ++i) {
        sum += task->data[i];
    }
    task->partial_sum = sum;
    return NULL;
}

int main(void) {
    // 1. Ініціалізація тестового масиву
    int *array = malloc(ARRAY_SIZE * sizeof(int));
    if (!array) return EXIT_FAILURE;
    for (int i = 0; i < ARRAY_SIZE; ++i) array[i] = 1;

    size_t mid = ARRAY_SIZE / 2;

    printf("--- ВАРІАНТ 1: Обчислення через ПОТОКИ (Shared Memory) ---\n");
    ThreadTask task = { .data = array, .start = mid, .end = ARRAY_SIZE, .partial_sum = 0 };
    pthread_t thread;

    // Створюємо потік: він читає той самий масив за прямим покажчиком
    pthread_create(&thread, NULL, thread_worker, &task);

    // Головний потік обчислює першу половину
    long long main_sum = 0;
    for (size_t i = 0; i < mid; ++i) main_sum += array[i];

    pthread_join(thread, NULL);
    long long total_thread_sum = main_sum + task.partial_sum;
    printf("Результат через потоки: %lld\n\n", total_thread_sum);

    printf("--- ВАРІАНТ 2: Обчислення через ПРОЦЕСИ (Fork + Pipe) ---\n");
    int pipefd[2];
    if (pipe(pipefd) < 0) { free(array); return EXIT_FAILURE; }

    pid_t pid = fork();
    if (pid == 0) {
        // Дочірній процес: обчислює другу половину
        close(pipefd[0]); // Закриваємо кінець для читання
        long long child_sum = 0;
        for (size_t i = mid; i < ARRAY_SIZE; ++i) child_sum += array[i];

        // Передаємо результат батькові через системний канал
        write(pipefd[1], &child_sum, sizeof(child_sum));
        close(pipefd[1]);
        free(array);
        _exit(EXIT_SUCCESS);
    }

    // Батьківський процес
    close(pipefd[1]); // Закриваємо кінець для запису
    long long proc_main_sum = 0;
    for (size_t i = 0; i < mid; ++i) proc_main_sum += array[i];

    long long proc_child_sum = 0;
    read(pipefd[0], &proc_child_sum, sizeof(proc_child_sum));
    close(pipefd[0]);
    waitpid(pid, NULL, 0);

    long long total_proc_sum = proc_main_sum + proc_child_sum;
    printf("Результат через процеси: %lld\n", total_proc_sum);

    free(array);
    return EXIT_SUCCESS;
}
