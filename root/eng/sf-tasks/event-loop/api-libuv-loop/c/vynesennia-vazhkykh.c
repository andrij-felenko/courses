#include <stdio.h>
#include <stdlib.h>
#include <uv.h>

void heavy_work_task(uv_work_t *req) {
    // Виконується у фоновому потоці з пулу робітників!
    long sum = 0;
    for (long i = 0; i < 100000000L; ++i) {
        sum += i;
    }
    req->data = (void*)sum;
}

void on_work_completed(uv_work_t *req, int status) {
    // Виконується у головному потоці циклу подій!
    printf("Фонову задачу завершено, результат: %ld
", (long)req->data);
    free(req);
}

int main(void) {
    uv_loop_t *loop = uv_default_loop();

    uv_work_t *req = malloc(sizeof(uv_work_t));
    uv_queue_work(loop, req, heavy_work_task, on_work_completed);

    printf("Головний цикл подій запущено...
");
    uv_run(loop, UV_RUN_DEFAULT);

    uv_loop_close(loop);
    return 0;
}
