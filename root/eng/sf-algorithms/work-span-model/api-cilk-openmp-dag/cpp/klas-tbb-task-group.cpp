#include <iostream>
#include <tbb/task_group.h>

void parallel_recursive_fibonacci(int n, int &result) {
    if (n < 2) {
        result = n;
        return;
    }

    int left_res = 0;
    int right_res = 0;
    tbb::task_group tg;

    // Створення лівої підзадачі (spawn)
    tg.run([n, &left_res] {
        parallel_recursive_fibonacci(n - 1, left_res);
    });

    // Створення правої підзадачі (spawn)
    tg.run([n, &right_res] {
        parallel_recursive_fibonacci(n - 2, right_res);
    });

    // Синхронізація обох підзадач (sync)
    tg.wait();

    result = left_res + right_res;
}
