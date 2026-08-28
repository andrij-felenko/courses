std::mutex m1, m2;

// 1. std::defer_lock — створити обгортку, але не захоплювати замок зараз
std::unique_lock<std::mutex> lock1(m1, std::defer_lock);
std::unique_lock<std::mutex> lock2(m2, std::defer_lock);
// Захопити обидва одночасно за алгоритмом уникнення дедлоку
std::lock(lock1, lock2);

// 2. std::try_to_lock — спробувати захопити через try_lock()
std::unique_lock<std::mutex> try_l(m1, std::try_to_lock);
if (try_l.owns_lock()) {
    // Критична секція успішно захоплена
}

// 3. std::adopt_lock — повідомити обгортці, що замок ВЖЕ захоплено раніше
m1.lock();
std::lock_guard<std::mutex> adopt_g(m1, std::adopt_lock);
// Тепер adopt_g відповідає за звільнення m1 у деструкторі
