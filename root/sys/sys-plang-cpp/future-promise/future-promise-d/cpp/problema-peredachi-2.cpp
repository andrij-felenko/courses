#include <thread>
#include <mutex>
#include <condition_variable>
#include <exception>
#include <iostream>

struct ManualChannel {
    std::mutex mtx;
    std::condition_variable cv;
    bool ready = false;
    int result = 0;
    std::exception_ptr ex = nullptr;
};

void worker(ManualChannel& ch) {
    try {
        int res = compute_payload();
        {
            std::lock_guard<std::mutex> lock(ch.mtx);
            ch.result = res;
            ch.ready = true;
        }
        ch.cv.notify_one();
    } catch (...) {
        {
            std::lock_guard<std::mutex> lock(ch.mtx);
            ch.ex = std::current_exception();
            ch.ready = true;
        }
        ch.cv.notify_one();
    }
}
