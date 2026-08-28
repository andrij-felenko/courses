template <class Lock, class Predicate>
bool wait(Lock& lock, std::stop_token stoken, Predicate pred) {
    while (!pred()) {
        if (stoken.stop_requested()) {
            return pred(); // Якщо скасовано — негайно повертаємо стан предиката
        }

        // Реєструємо тимчасовий колбек на час сну
        std::stop_callback cb(stoken, [this] {
            notify_all(); // Сповіщаємо умовну змінну при надходженні сигналу
        });

        // Відпускаємо замок та переходимо в стан сну в ядрі ОС
        wait_internal(lock);
    }
    return true;
}
