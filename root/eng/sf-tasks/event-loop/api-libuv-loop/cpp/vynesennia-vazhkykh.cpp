#include <iostream>
#include <memory>
#include <uv.h>

struct WorkTask {
    uv_work_t req;
    long result{0};
};

int main() {
    uv_loop_t* loop = uv_default_loop();

    auto task = std::make_unique<WorkTask>();
    task->req.data = task.get();

    auto work_cb = [](uv_work_t* req) {
        // Виконується у фоновому потоці з пулу робітників!
        auto* t = static_cast<WorkTask*>(req->data);
        long sum = 0;
        for (long i = 0; i < 100000000L; ++i) {
            sum += i;
        }
        t->result = sum;
    };

    auto after_work_cb = [](uv_work_t* req, int status) {
        // Виконується у головному потоці циклу подій!
        auto* t = static_cast<WorkTask*>(req->data);
        std::cout << "Фонову задачу завершено, результат: " << t->result << std::endl;
        delete t;
    };

    auto* raw_task = task.release();
    uv_queue_work(loop, &raw_task->req, work_cb, after_work_cb);

    std::cout << "Головний цикл подій запущено...
";
    uv_run(loop, UV_RUN_DEFAULT);

    uv_loop_close(loop);
    return 0;
}
