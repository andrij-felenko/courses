// Функція з підтримкою кооперативного скасування у C++20
int cancellable_task(std::stop_token stop_tok, int target) {
    for (int i = 0; i < target; ++i) {
        if (stop_tok.stop_requested()) {
            std::cout << "Задачу скасовано на кроці " << i << std::endl;
            return -1;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return target * 2;
}
