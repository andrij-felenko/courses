// Концептуальна модель черги мікрозадач у C++
#include <iostream>
#include <queue>
#include <functional>

class MicrotaskScheduler {
public:
    void enqueue_microtask(std::function<void()> task) {
        microtasks_.push(std::move(task));
    }

    void drain_microtasks() {
        // УВАГА: Якщо таска додасть нову таску, цикл не вийде,
        // блокуючи основні фази I/O (Microtask Starvation)!
        while (!microtasks_.empty()) {
            auto task = std::move(microtasks_.front());
            microtasks_.pop();
            task();
        }
    }

private:
    std::queue<std::function<void()>> microtasks_;
};
