auto deadline = std::chrono::steady_clock::now() + 100ms;

std::unique_lock<std::mutex> lock(mtx);
// wait_until використовує фіксовану абсолютну часову точку
while (!ready) {
    if (cv.wait_until(lock, deadline) == std::cv_status::timeout) {
        if (!ready) {
            std::cout << "Точний таймаут досягнуто!\n";
            break;
        }
    }
}
