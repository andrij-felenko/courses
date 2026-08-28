std::mutex mtx;
std::condition_variable cv;
bool ready = false;

// Потік A (Споживач)
void worker() {
    std::unique_lock<std::mutex> lock(mtx);
    // wait() атомарно відпускає mtx і блокує потік
    cv.wait(lock, []{ return ready; });
    // Після повернення з wait() м'ютекс mtx ЗНОВУ ЗАХОПЛЕНИЙ потоком A!
}
