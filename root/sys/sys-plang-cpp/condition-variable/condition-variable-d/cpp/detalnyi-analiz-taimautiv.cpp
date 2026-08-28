using namespace std::chrono_literals;

std::unique_lock<std::mutex> lock(mtx);

// Очікування з відносним таймаутом (100 мілісекунд)
if (cv.wait_for(lock, 100ms, []{ return ready; })) {
    std::cout << "Подія настала вчасно!\n";
} else {
    std::cout << "Таймаут вичерпано, подія не настала.\n";
}
