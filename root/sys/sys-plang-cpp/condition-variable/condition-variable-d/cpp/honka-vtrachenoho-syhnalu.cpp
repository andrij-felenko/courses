// ✗ ПОМИЛКОВА СХЕМА: Спроба симуляції очікування без condition_variable
std::mutex mtx;
bool ready = false;

// Потік A (Споживач)
void worker() {
    std::unique_lock<std::mutex> lock(mtx);
    if (!ready) {
        lock.unlock(); // (1) Відпустили м'ютекс
        
        // ─── КРИТИЧНЕ ВІКНО ГОНКИ ───
        // Потік B може вклинитися СЮДИ!
        
        sleep_until_signaled(); // (2) Заснули
    }
}

// Потік B (Виробник)
void publisher() {
    {
        std::lock_guard<std::mutex> lock(mtx);
        ready = true; // (3) Змінили стан
    }
    send_signal(); // (4) Надіслали сигнал
}
